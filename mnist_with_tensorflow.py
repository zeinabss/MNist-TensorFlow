# -*- coding: utf-8 -*-
"""MNIST with TensorFlow.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1CC87HMnUzkKxryx9e2_9fCFyEp15mswN
"""

#import libraries
import math
import numpy as np
import h5py
import matplotlib.pyplot as plt
import scipy
from PIL import Image
from scipy import ndimage
import tensorflow as tf
from tensorflow.python.framework import ops
from helper import *

(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
np.random.seed(1)


# Commented out IPython magic to ensure Python compatibility.
#display samples of the train dataset
import matplotlib.pyplot as plt
# %matplotlib inline 
image_index = -1 
fig=plt.figure(figsize=(8, 8))
columns = 3
rows = 3
for i in range(1, columns*rows +1):
    fig.add_subplot(rows, columns, i)
    plt.imshow(x_train[image_index+i],cmap='gray')

    
#preprocess the datasets
X_train = x_train/255.
X_test = x_test/255.

#convert the labels into one_hot representation
Y_train = convert_to_one_hot(y_train, 10)
Y_test = convert_to_one_hot(y_test, 10)

#reshape the dataset - so the network knows it's an image
X_train = X_train.reshape(X_train.shape[0], 28, 28, 1)
X_test = X_test.reshape(X_test.shape[0], 28, 28, 1)

#check the shape of the dataset
print ("number of training examples = " + str(X_train.shape[0]))
print ("number of test examples = " + str(X_test.shape[0]))
print ("X_train shape: " + str(X_train.shape))
print ("Y_train shape: " + str(Y_train.shape))
print ("X_test shape: " + str(X_test.shape))
print ("Y_test shape: " + str(Y_test.shape))

#Function to create placeholders for X and Y 
def create_placeholders(n_H0, n_W0, n_C0, n_y):

    X = tf.placeholder(tf.float32,shape=(None,n_H0,n_W0,n_C0))
    Y = tf.placeholder(tf.float32,shape=(None,n_y))
    
    return X, Y
  
#Function to initialize parameters
def initialize_parameters():
    
    tf.set_random_seed(1)      

    W1 = tf.get_variable("W1", [8, 8, 1, 8], initializer =  tf.contrib.layers.xavier_initializer(seed = 0))
    W2 = tf.get_variable("W2", [4, 4, 8, 16], initializer =  tf.contrib.layers.xavier_initializer(seed = 0))
    W3 = tf.get_variable("W3", [2, 2, 16, 32], initializer =  tf.contrib.layers.xavier_initializer(seed = 0))

    parameters = {"W1": W1,
                  "W2": W2,
                  "W3": W3}
    
    return parameters
  
  
#Function to create the forward propogation (layers are added in this function)
def forward_propagation(X, parameters):
    
    #initialize weights of the conv filters
    W1 = parameters['W1']
    W2 = parameters['W2']
    W3 = parameters['W3']

    
    Z1 = tf.nn.conv2d(X,W1, strides = [1,1,1,1], padding = 'SAME')

    A1 = tf.nn.relu(Z1)

    P1 = tf.nn.max_pool(A1, ksize = [1,8,8,1], strides = [1,8,8,1], padding = 'SAME')

    Z2 = tf.nn.conv2d(P1,W2, strides = [1,1,1,1], padding = 'SAME')

    A2 = tf.nn.relu(Z2)

    P2 = tf.nn.max_pool(A2, ksize = [1,4,4,1], strides = [1,4,4,1], padding = 'SAME')
    
    Z3 = tf.nn.conv2d(P2,W3, strides = [1,1,1,1], padding = 'SAME')

    A3 = tf.nn.relu(Z3)

    P3 = tf.nn.max_pool(A3, ksize = [1,2,2,1], strides = [1,2,2,1], padding = 'SAME')

    P3 = tf.layers.flatten(A3)
    
    #the output layer
    Z4 = tf.contrib.layers.fully_connected(P3, 10, activation_fn=None)

    return Z4
  
  
#Function to create the model, and define hyperparameters
def model(X_train, Y_train, X_test, Y_test, optimizer='adam', learning_rate = 0.001,
          num_epochs = 150, minibatch_size = 64, print_cost = True):
    
    
    ops.reset_default_graph()                         
    tf.set_random_seed(1)                             
    seed = 3                                          
    (m, H, W, C) = X_train.shape             
    n_y = Y_train.shape[1]                            
    costs = []                                        
    
    X, Y = create_placeholders(H, W, C, n_y)

    parameters = initialize_parameters()

    Z = forward_propagation(X, parameters)
    
    cost =tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits = Z, labels = Y))

    if optimizer=='adagrad':
        optimizer = tf.train.AdagradOptimizer(learning_rate = learning_rate).minimize(cost)
    elif optimizer=='adagradda':
        optimizer = tf.train.AdagradDAOptimizer(learning_rate = learning_rate).minimize(cost)
    elif optimizer=='adadelta':
        optimizer = tf.train.AdadeltaOptimizer(learning_rate = learning_rate).minimize(cost)
    elif optimizer=='adam':
        optimizer = tf.train.AdamOptimizer(learning_rate = learning_rate).minimize(cost)

    init = tf.global_variables_initializer()
   
    with tf.Session() as sess:

        sess.run(init)
        #mini batch train 
        for epoch in range(num_epochs):

            minibatch_cost = 0.
            num_minibatches = int(m / minibatch_size) 
            seed = seed + 1
            minibatches = random_mini_batches(X_train, Y_train, minibatch_size, seed)

            for minibatch in minibatches:

                (minibatch_X, minibatch_Y) = minibatch
                _ , temp_cost = sess.run([optimizer, cost], feed_dict={X: minibatch_X, Y: minibatch_Y})
                
                minibatch_cost += temp_cost / num_minibatches
                

            if print_cost == True and epoch % 5 == 0:
                print ("Cost after epoch %i: %f" % (epoch, minibatch_cost))
            if print_cost == True and epoch % 1 == 0:
                costs.append(minibatch_cost)
        
        #plot the cost over epochs
        plt.plot(np.squeeze(costs))
        plt.ylabel('cost')
        plt.xlabel('iterations (per tens)')
        plt.title("Learning rate =" + str(learning_rate))
        plt.show()

        # Calculate the correct predictions
        correct_prediction = tf.equal(tf.argmax(Z, 1), tf.argmax(Y, 1))
        
        # Calculate accuracy on the test set
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
        print(accuracy)
        train_accuracy = accuracy.eval({X: X_train, Y: Y_train})
        test_accuracy = accuracy.eval({X: X_test, Y: Y_test})
        print("Train Accuracy:", train_accuracy)
        print("Test Accuracy:", test_accuracy)
                
        return train_accuracy, test_accuracy, parameters


train_accuracy, text_accuracy, parameters = model(X_train, Y_train, X_test, Y_test)

