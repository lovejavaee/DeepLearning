#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
 Deep Belief Nets
'''

import sys
import numpy
from HiddenLayer import HiddenLayer
from LogisticRegression import LogisticRegression
from RestrictedBoltzmannMachine import RBM
from utils import *


class DBN(object):
    def __init__(self, input=None, n_ins=2, hidden_layer_sizes=[3, 3], n_outs=2, \
                 numpy_rng=None):   # constructor does not contain input
        
        self.input = input

        self.sigmoid_layers = []
        self.rbm_layers = []
        self.n_layers = len(hidden_layer_sizes)  # = len(self.rbm_layers)

        if numpy_rng is None:
            numpy_rng = numpy.random.RandomState(1234)
        

        assert self.n_layers > 0


        # construct multi-layer
        for i in xrange(self.n_layers):
            # layer_size
            if i == 0:
                input_size = n_ins
            else:
                input_size = hidden_layer_sizes[i - 1]

            # layer_input
            if i == 0:
                layer_input = self.input
            else:
                layer_input = self.sigmoid_layers[-1].output()
                
            # construct sigmoid_layer
            sigmoid_layer = HiddenLayer(input=layer_input,
                                        n_in=input_size,
                                        n_out=hidden_layer_sizes[i],
                                        numpy_rng=numpy_rng,
                                        activation=sigmoid)
            self.sigmoid_layers.append(sigmoid_layer)


            # construct rbm_layer
            rbm_layer = RBM(input=layer_input,
                            n_visible=input_size,
                            n_hidden=hidden_layer_sizes[i],
                            W=sigmoid_layer.W,     # W, b are shared
                            hbias=sigmoid_layer.b)
            self.rbm_layers.append(rbm_layer)


        # exit()


        # layer for output using Logistic Regression
        self.log_layer = LogisticRegression(input=self.sigmoid_layers[-1].output(),
                                            n_in=hidden_layer_sizes[-1],
                                            n_out=n_outs)

        # finetune cost: the negative log likelihood of the logistic regression layer
        # self.finetune_cost = self.log_layer.negative_log_likelihood()
        # print self.finetune_cost


        # self.errors



    def pretrain(self, lr=0.1, k=1, epochs=100):
        # pre-train layer-wise
        for i in xrange(self.n_layers):
            if i == 0:
                layer_input = self.input
            else:
                layer_input = self.sigmoid_layers[i-1].output()
            rbm = self.rbm_layers[i]

            
            for epoch in xrange(epochs):
                c = []
                rbm.contrastive_divergence(lr=lr, k=k, input=layer_input)
                cost = rbm.get_reconstruction_cross_entropy()
                # c.append(cost)
                print >> sys.stderr, \
                      'Pre-training layer %d, epoch %d, cost ' %(i, epoch), cost
                
                # print numpy.mean(c)


    def finetune(self, y, lr=0.1, epochs=100):
        layer_input = self.sigmoid_layers[-1].output()

        # train log_layer
        epoch = 0
        done_looping = False
        while (epoch < epochs) and (not done_looping):
            self.log_layer.train(y=y, lr=lr, input=layer_input)
            cost = self.log_layer.negative_log_likelihood(y=y)
            print >> sys.stderr, 'Training epoch %d, cost is ' % epoch, cost
            
            lr *= 0.95
            epoch += 1

        # print self.log_layer.W
        # exit()

    def predict(self, x):
        layer_input = x
        
        for i in xrange(self.n_layers):
            print layer_input
            sigmoid_layer = self.sigmoid_layers[i]
            layer_input = sigmoid_layer.output(input=layer_input)

        # print self.log_layer.W
        out = self.log_layer.predict(layer_input)
        print layer_input
        
        return out


def test_dbn(pretrain_lr=0.1, pretraining_epochs=10, k=1, \
             finetune_lr=0.1, finetune_epochs=10):
    
    x = numpy.array([[0, 0, 0, 1],
                     [0, 0, 1, 0],
                     [0, 0, 1, 0],
                     [0, 1, 0, 0],
                     [0, 1, 0, 0],
                     [1, 0, 0, 0]])
    y = numpy.array([[0, 0, 0, 1],
                     [0, 0, 1, 0],
                     [0, 0, 1, 0],
                     [0, 1, 0, 0],
                     [0, 1, 0, 0],
                     [1, 0, 0, 0]])
    
    rng = numpy.random.RandomState(123)

    # construct DBN
    dbn = DBN(input=x, n_ins=4, hidden_layer_sizes=[10], n_outs=4, numpy_rng=rng)

    # pre-training (TrainUnsupervisedDBN)
    dbn.pretrain(lr=pretrain_lr, k=1, epochs=pretraining_epochs)
    
    # fine-tuning (DBNSupervisedFineTuning)
    dbn.finetune(y, lr=finetune_lr, epochs=finetune_epochs)


    # test
    x = numpy.array([0, 0, 0, 1])
    print dbn.predict(x)   # 0
    print 


    exit()
    x = numpy.array([0, 0])
    print dbn.predict(x)   # 0
    print 
    x = numpy.array([0, 1])
    print dbn.predict(x)   # 1
    print 
    x = numpy.array([1, 0])
    print dbn.predict(x)   # 1
    print 
    x = numpy.array([1, 1])
    print dbn.predict(x)   # 0

if __name__ == "__main__":
    test_dbn()