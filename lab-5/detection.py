from cnn import CNN_MAL
from rnn import RNN_MAL
from gnn import GNN_MAL
import config
import pickle
import glob
import numpy as np
import tensorflow as tf
from text_iterator import text_iterator
from graph_iterator import *
from tf_utils import check_distribution

# print(tf.executing_eagerly())


def prepare_data_image(tensor=True):
    with open(config.CFG_split_data, "rb") as jf:
        train_set, test_set, train_lbs, test_lbs = pickle.load(jf)
    b = glob.glob("data/L/Benign/*")
    v = glob.glob("data/L/Virus/*")
    alls = b + v
    check_distribution(train_set, alls)
    check_distribution(test_set, alls)
    train_set = [alls[f] for f in train_set]
    test_set = [alls[f] for f in test_set]  # [:50]
    check_distribution(train_set)
    check_distribution(test_set)

    def _parsefunc(filename, lbs):
        img_st = tf.io.read_file(filename)
        img_dec = tf.io.decode_png(img_st, channels=config.channel)
        img = tf.cast(img_dec, tf.float32) / 255.0
        img = tf.image.resize(
            img, [config.img_height, config.img_height], method="bilinear"
        )
        return img, lbs

    def convert_dataset(train_set, train_lbs, _parsefunc, batch_size=config.batch_size):
        AUTOTUNE = tf.data.experimental.AUTOTUNE
        ds = tf.data.Dataset.from_tensor_slices((train_set, train_lbs))
        train_ds = ds.map(_parsefunc)
        train_ds = train_ds.batch(batch_size)
        train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
        return train_ds

    return convert_dataset(train_set, train_lbs, _parsefunc), convert_dataset(
        test_set, test_lbs, _parsefunc, 1
    )


def prepare_data_txt():
    with open(config.CFG_split_data, "rb") as jf:
        train_set, test_set, _, _ = pickle.load(jf)
    b = glob.glob("data/Seq-ori/Benign/*")
    v = glob.glob("data/Seq-ori/Virus/*")
    alls = b + v
    check_distribution(train_set, alls)
    check_distribution(test_set, alls)
    train_set = [alls[f] for f in train_set]
    test_set = [alls[f] for f in test_set]  # [:50]
    check_distribution(train_set)
    check_distribution(test_set)
    print(len(train_set), len(test_set))
    train_ds = text_iterator(train_set, 1, config.batch_size)
    test_ds = text_iterator(test_set, 1, config.batch_size, shuffle=False)
    return train_ds, test_ds


def prepare_data_graph():
    with open(config.graph_data, "rb") as jf:
        g_list = pickle.load(jf)
    with open(config.CFG_split_data, "rb") as jf:
        train_set, test_set, _, _ = pickle.load(jf)
    print(len(train_set), len(test_set))
    return [g_list[i] for i in train_set], [g_list[i] for i in test_set]


def cnn_model(load=""):
    model = CNN_MAL(config.num_classes)
    model.compile(
        optimizer="adam",
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"],
    )
    if load != "":
        _, ckpt_manager = load_ckpt(model, config.model_save_path + load + "/")
    return model


def rnn_model(name, load=""):
    model = RNN_MAL(config.num_classes, name)
    model.compile(
        optimizer="adam",
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["acc"],
    )
    if load != "":
        _, ckpt_manager = load_ckpt(model, config.model_save_path + load + "/")
    return model


def gnn_model(load=""):
    model = GNN_MAL(config.num_classes)
    if load != "":
        _, ckpt_manager = load_ckpt(model, config.model_save_path + load + "/")
    return model


fn = tf.keras.metrics.FalseNegatives()
fp = tf.keras.metrics.FalsePositives()
tn = tf.keras.metrics.TrueNegatives()
tp = tf.keras.metrics.TruePositives()
acc = tf.keras.metrics.Accuracy()
recall = tf.keras.metrics.Recall()


def metrics(y_true, y_pred):
    print(
        fn(y_true, y_pred),
        fp(y_true, y_pred),
        tn(y_true, y_pred),
        tp(y_true, y_pred),
        recall(y_true, y_pred),
        acc(y_true, y_pred),
    )
    fp.reset_states()
    fn.reset_states()
    tp.reset_states()
    tn.reset_states()
    acc.reset_states()
    recall.reset_states()


def train(name):
    if name == "cnn":
        train_ds, val_ds = prepare_data_image()
        model = cnn_model()
    elif name == "lstm" or name == "gru" or name == "rnn":
        train_ds, val_ds = prepare_data_txt()
        model = rnn_model(name)
    elif name == "gnn":
        train_ds, val_ds = prepare_data_graph()
        model = gnn_model()

    _, ckpt_manager = load_ckpt(model, config.model_save_path + name + "/")
    _max_acc = 0.90
    if name == "gnn":
        for _ in range(config.epochs):
            gnn_train(model, train_ds)
            y_true, y_pred = gnn_test(model, val_ds)
            metrics(y_true, y_pred)
            ckpt_manager.save()
    else:
        for i in range(config.epochs):
            print("===========\n", i)
            history = model.fit(
                train_ds,
                validation_data=val_ds,
                batch_size=config.batch_size,
                # steps_per_epoch=config.train_size/config.batch_size,
                epochs=5,  # config.epochs
            )
            if history.history["val_accuracy"][0] > _max_acc:
                _max_acc = history.history["val_accuracy"][0]
                ckpt_manager.save()


def evaluation(name):
    if name == "cnn":
        _, val_ds = prepare_data_image()
        model = cnn_model(name)
    elif name == "lstm" or name == "gru" or name == "rnn":
        _, val_ds = prepare_data_txt()
        model = rnn_model(name, name)
    elif name == "gnn":
        _, val_ds = prepare_data_graph()
        model = gnn_model(name)

    if name == "gnn":
        y_true, y_pred = gnn_test(model, val_ds)
        metrics(y_true, y_pred)
    elif name == "lstm" or name == "gru" or name == "rnn":
        y_pred = model.predict(val_ds)
        y_pred = tf.reshape(tf.argmax(y_pred, axis=1), shape=(-1))
        y_true = val_ds.get_labels()
        y_true = tf.concat(y_true, 0)
        metrics(y_true, y_pred)
    else:
        y_pred = model.predict(val_ds)
        model.save(config.model_save_path + name + "/single.model")
        y_pred = tf.reshape(tf.argmax(y_pred, axis=1), shape=(-1))
        y_true = []
        for element in val_ds.as_numpy_iterator():
            y_true.append(element[1])
        y_true = tf.concat(y_true, 0)
        metrics(y_true, y_pred)


def load_ckpt(model, path, newest=True):
    ckpt = tf.train.Checkpoint(transformer=model)
    ckpt_manager = tf.train.CheckpointManager(ckpt, path, max_to_keep=5)
    if ckpt_manager.latest_checkpoint:
        if newest == True:
            ckpt.restore(ckpt_manager.latest_checkpoint)
            print(
                "Latest checkpoint restored!!",
                path,
                newest,
                ckpt_manager.latest_checkpoint,
            )
        else:
            ckpt.restore(path + newest)
            print("checkpoint restored!!", path, newest)
    return ckpt, ckpt_manager


if __name__ == "__main__":
    train("cnn")
    # train('rnn')
    # train('gnn')
    evaluation("cnn")
