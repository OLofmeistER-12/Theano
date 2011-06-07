import numpy
import unittest
from theano.tests import unittest_tools as utt
import theano
import theano.tensor as T

class Test_incsubtensor(unittest.TestCase):
    """Partial testing.

    What could be tested:
    - increment vs set
    - thing incremented: scalar, vector, matrix,
    - increment/set: constant, scalar, vector, matrix
    - indices: scalar vs slice, constant vs variable, out of bound, ...
    - inplace
    """
    def setUp(self):
        utt.seed_rng()

    def test_simple_ok(self):
        """Increments or sets part of a tensor by a scalar using full slice and
        a partial slice depending on a scalar.
        """
        a = T.dmatrix()
        increment = T.dscalar()
        sl1 = slice(None)
        sl2_end = T.lscalar()
        sl2 = slice(sl2_end)

        for do_set in [False,True]:

            if do_set:
                resut = T.setsubtensor(a, increment, [sl1, sl2])
            else:
                resut = T.incsubtensor(a, increment, [sl1, sl2])

            f = theano.function([a, increment, sl2_end], resut)

            val_a = numpy.ones((5,5))
            val_inc = 2.3
            val_sl2_end = 2

            result = f(val_a, val_inc, val_sl2_end)

            expected_result = numpy.copy(val_a)
            if do_set:
                expected_result[:,:val_sl2_end] = val_inc
            else:
                expected_result[:,:val_sl2_end] += val_inc

            self.assertTrue(numpy.array_equal(result, expected_result))
        return

    def test_grad(self):


        a = T.dvector()
        b = T.dvector()

        def inc_slice(*s):
            def just_numeric_args(a,b):
                return T.incsubtensor(a, b, s)
            return just_numeric_args

        # vector
        utt.verify_grad(
                inc_slice(slice(2,4,None)),
                (numpy.asarray([0,1,2,3,4,5.]),
                    numpy.asarray([9,9.]),))

        # matrix
        utt.verify_grad(
                inc_slice(slice(1,2,None), slice(None, None, None)),
                (numpy.asarray([[0,1],[2,3],[4,5.]]),
                    numpy.asarray([[9,9.]]),))

        #single element
        utt.verify_grad(
                inc_slice(2, 1),
                (numpy.asarray([[0,1],[2,3],[4,5.]]),
                    numpy.asarray(9.),))
