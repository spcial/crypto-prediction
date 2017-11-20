#!/usr/bin/python
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import urllib.request, json

from bot.shared_config import *

def main():
    start_time = time.time()

    dump(yellow("Retrieving market data from API"))

    with urllib.request.urlopen("https://api.kraken.com/0/public/OHLC?pair=ETHUSD&interval=15") as url:
        data = json.loads(url.read().decode())
        timestamps = []
        prices = []
        volumes = []
        pricevol = []

        for set in data["result"]['XETHZUSD'][-601:]:
            timestamps.append(int(set[0]))
            prices.append(float(set[4]))
            volumes.append(float(set[6]))
            pricevol.append([float(set[4]), float(set[6])])

    dump(green("Retrieved API in {0:.3f}ms sec".format((time.time() - start_time)*100)))
    dump(yellow("Initialize Tensorflow"))

    f_horizon = 1  # forecast horizon, one period into the future
    num_periods = 20  # number of periods per vector we are using to predict one period ahead
    inputs = 2  # number of vectors submitted
    hidden = 100  # number of neurons we will recursively work through, can be changed to improve accuracy
    output = 1  # number of output vectors

    TS = np.array(pricevol)
    TSo = np.array(prices)

    x_data = TS[:(len(TS) - (len(TS) % num_periods))]
    x_batches = x_data.reshape(-1, 20, 2)

    y_data = TSo[1:(len(TSo) - (len(TSo) % num_periods)) + f_horizon]
    y_batches = y_data.reshape(-1, 20, 1)

    def test_data(forecast, num_periods):
        test_x_setup = TS[-(num_periods + forecast):]
        testX = test_x_setup[:num_periods].reshape(-1, 20, 2)
        testY = TSo[-(num_periods):].reshape(-1, 20, 1)
        return testX, testY

    X_test, Y_test = test_data(f_horizon, num_periods)

    tf.reset_default_graph()  # We didn't have any previous graph objects running, but this would reset the graphs

    X = tf.placeholder(tf.float32, [None, num_periods, inputs])  # create variable objects
    y = tf.placeholder(tf.float32, [None, num_periods, output])

    basic_cell = tf.contrib.rnn.BasicRNNCell(num_units=hidden, activation=tf.nn.relu)  # create our RNN object
    rnn_output, states = tf.nn.dynamic_rnn(basic_cell, X, dtype=tf.float32)  # choose dynamic over static

    learning_rate = 0.001  # small learning rate so we don't overshoot the minimum

    stacked_rnn_output = tf.reshape(rnn_output, [-1, hidden])  # change the form into a tensor
    stacked_outputs = tf.layers.dense(stacked_rnn_output, output)  # specify the type of layer (dense)
    outputs = tf.reshape(stacked_outputs, [-1, num_periods, output])  # shape of results

    loss = tf.reduce_sum(tf.square(outputs - y))  # define the cost function which evaluates the quality of our model
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)  # gradient descent method
    training_op = optimizer.minimize(
        loss)  # train the result of the application of the cost_function

    init = tf.global_variables_initializer()  # initialize all the variables

    epochs = 1000  # number of iterations or training cycles, includes both the FeedFoward and Backpropogation

    with tf.Session() as sess:
        init.run()
        dump(green("Initialized Tensorflow in {0:.3f}ms sec".format((time.time() - start_time) * 100)))
        dump(yellow("Start Training"))

        for ep in range(epochs):
            sess.run(training_op, feed_dict={X: x_batches, y: y_batches})
            if ep % 100 == 0:
                mse = loss.eval(feed_dict={X: x_batches, y: y_batches})
                print(ep, "\tMSE:", mse)

        dump(green("Finished training in {0:.3f}ms sec".format((time.time() - start_time) * 100)))

        dump(yellow("Start Predicting"))
        y_pred = sess.run(outputs, feed_dict={X: X_test})
        dump(green("Prediction finished in {0:.3f}ms sec".format((time.time() - start_time) * 100)))

    dump(yellow("Start Plotting and output"))

    actual_series = pd.Series(np.concatenate([np.ravel(X_test)[::2],np.ravel(Y_test)]))
    actual_prediction = pd.Series(np.concatenate([np.ravel(X_test)[::2],np.ravel(y_pred)]))

    plt.title("Forecast vs Actual", fontsize=14)
    plt.plot(actual_series, "b-", markersize=10, label="Actual")
    # plt.plot(pd.Series(np.ravel(Y_test)), "w*", markersize=10)
    plt.plot(actual_prediction, "r-", markersize=7, label="Forecast")
    plt.legend(loc="upper left")
    plt.xlabel("Time Periods")

    dump(green("Finished complete program in {0:.3f}ms sec".format((time.time() - start_time) * 100)))
    plt.show()


if __name__ == '__main__':
        print("Starting prediction ...")
        main()
