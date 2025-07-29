# test_fimo.py
# Contact: Jacob Schreiber <jmschreiber91@gmail.com>

import numpy
import pytest
import pandas

from memelite.fimo import _pwm_to_mapping
from memelite.fimo import fimo
from memelite.io import read_meme

from numpy.testing import assert_raises
from numpy.testing import assert_array_equal
from numpy.testing import assert_array_almost_equal


def random_one_hot(shape, probs=None, dtype='int8', random_state=None):
	if not isinstance(shape, tuple) or len(shape) != 3:
		raise ValueError("Shape must be a tuple with 3 dimensions.")

	if not isinstance(random_state, numpy.random.RandomState):
		random_state = numpy.random.RandomState(random_state)

	if isinstance(probs, list):
		probs = numpy.array(probs)
		
	n = shape[1]
	ohe = numpy.zeros(shape, dtype=dtype)

	for i in range(ohe.shape[0]):
		if probs is None:
			probs_ = None
		elif probs.ndim == 1:
			probs_ = probs
		elif probs.shape[0] == 1:
			probs_ = probs[0]
		else:
			probs_ = probs[i] 

		choices = random_state.choice(n, size=shape[2], p=probs_)
		ohe[i, choices, numpy.arange(shape[2])] = 1 

	return one


###


@pytest.fixture
def log_pwm():
	r = numpy.random.RandomState(0)

	pwm = numpy.exp(r.randn(4, 14))
	pwm = pwm / pwm.sum(axis=0, keepdims=True)
	return numpy.log2(pwm)

@pytest.fixture
def short_log_pwm():
	r = numpy.random.RandomState(0)

	pwm = numpy.exp(r.randn(4, 2))
	pwm = pwm / pwm.sum(axis=0, keepdims=True)
	return numpy.log2(pwm)

@pytest.fixture
def long_log_pwm():
	r = numpy.random.RandomState(0)

	pwm = numpy.exp(r.randn(4, 50))
	pwm = pwm / pwm.sum(axis=0, keepdims=True)
	return numpy.log2(pwm)


###


def test_pwm_to_mapping(log_pwm):
	smallest, mapping = _pwm_to_mapping(log_pwm, 0.1)

	assert smallest == -596
	assert mapping.shape == (600,)
	assert mapping.dtype == numpy.float64


	assert_array_almost_equal(mapping[:8], [7.4903e-08,  6.4154e-08,  
		4.2656e-08,  2.1158e-08, -1.1089e-08, -6.4833e-08, -1.1858e-07, 
		-1.8307e-07], 4)
	assert_array_almost_equal(mapping[100:108], [-0.0082, -0.0087, -0.0093, 
		-0.0099, -0.0105, -0.0112, -0.0119, -0.0126], 4)
	assert_array_almost_equal([mapping[~numpy.isinf(mapping)].min()], 
		[-28.], 4) 

	assert numpy.all(numpy.diff(mapping[~numpy.isinf(mapping)]) <= 0)
	assert numpy.isinf(mapping).sum() == 117


def test_short_pwm_to_mapping(short_log_pwm):
	smallest, mapping = _pwm_to_mapping(short_log_pwm, 0.1)

	assert smallest == -78
	assert mapping.shape == (67,)
	assert mapping.dtype == numpy.float64

	assert_array_almost_equal(mapping[:8], [ 8.3267e-17, -9.3109e-02, 
		-1.9265e-01, -1.9265e-01, -1.9265e-01, -1.9265e-01, -1.9265e-01, 
		-1.9265e-01], 4)
	assert_array_almost_equal([mapping[~numpy.isinf(mapping)].min()], 
		[-4], 4) 

	assert numpy.all(numpy.diff(mapping[~numpy.isinf(mapping)]) <= 0)
	assert numpy.isinf(mapping).sum() == 6


def test_long_pwm_to_mapping(long_log_pwm):
	smallest, mapping = _pwm_to_mapping(long_log_pwm, 0.1)

	assert smallest == -2045
	assert mapping.shape == (2085,)
	assert mapping.dtype == numpy.float64

	assert_array_almost_equal(mapping[:8], [-9.79656934e-16, -7.45058160e-09, 
		-2.23517430e-08, -3.72529047e-08, -5.96046475e-08, -9.68575534e-08, 
		-1.34110461e-07, -1.78813951e-07], 4)
	assert_array_almost_equal(mapping[100:108], [-3.3035e-14, -3.8062e-14, 
		-4.4026e-14, -5.1093e-14, -5.9458e-14, -6.9351e-14, -8.1036e-14, 
		-9.4826e-14], 4)
	assert_array_almost_equal([mapping[~numpy.isinf(mapping)].min()], 
		[-99.], 4) 

	assert numpy.all(numpy.diff(mapping[~numpy.isinf(mapping)]) <= 0)
	assert numpy.isinf(mapping).sum() == 486


def test_pwm_to_mapping_small_bins(log_pwm):
	smallest, mapping = _pwm_to_mapping(log_pwm, 0.01)

	assert smallest == -5955
	assert mapping.shape == (5864,)
	assert mapping.dtype == numpy.float64

	assert_array_almost_equal(mapping[:8], [-4.5076e-07, -4.6939e-07, 
		-4.8429e-07, -4.9546e-07, -5.1036e-07, -5.2154e-07, -5.4017e-07, 
		-5.5134e-07], 4)
	assert_array_almost_equal(mapping[100:108], [-4.5076e-07, -4.6939e-07, 
		-4.8429e-07, -4.9546e-07, -5.1036e-07, -5.2154e-07, -5.4017e-07, 
		-5.5134e-07], 4)
	assert_array_almost_equal([mapping[~numpy.isinf(mapping)].min()], 
		[-28.], 4) 

	assert numpy.all(numpy.diff(mapping[~numpy.isinf(mapping)]) <= 0)
	assert numpy.isinf(mapping).sum() == 1038


def test_pwm_to_mapping_large_bins(log_pwm):
	smallest, mapping = _pwm_to_mapping(log_pwm, 1)

	assert smallest == -60
	assert mapping.shape == (74,)
	assert mapping.dtype == numpy.float64

	assert_array_almost_equal(mapping[:8], [-3.5277e-07, -3.9577e-07, 
		-8.0423e-07, -3.0078e-06, -1.1978e-05, -4.1823e-05, -1.2694e-04, 
		-3.4126e-04], 4)
	assert_array_almost_equal([mapping[~numpy.isinf(mapping)].min()], 
		[-27], 4) 

	assert numpy.all(numpy.diff(mapping[~numpy.isinf(mapping)]) <= 0)
	assert numpy.isinf(mapping).sum() == 22


##


def test_fimo():
	hits = fimo("tests/data/test.meme", "tests/data/test.fa")

	assert len(hits) == 12
	for df in hits:
		assert isinstance(df, pandas.DataFrame)
		assert df.shape[1] == 8
		assert tuple(df.columns) == ('motif_name', 'motif_idx', 'sequence_name', 
			'start', 'end', 'strand', 'score', 'p-value')

	assert hits[0].shape == (1, 8)
	assert hits[9].shape == (1, 8)

	assert hits[0]['motif_name'][0] == "MEOX1_homeodomain_1"
	assert hits[0]['sequence_name'][0] == 'chr7'
	assert hits[0]['start'][0] == 1350
	assert hits[0]['end'][0] == 1360
	assert hits[0]['strand'][0] == '+'
	assert round(hits[0]['score'][0], 4) == round(11.446572, 4)
	assert round(hits[0]['p-value'][0], 4) == round(0.000075, 4)


	assert hits[9]['motif_name'][0] == "FOXQ1_MOUSE.H11MO.0.C"
	assert hits[9]['sequence_name'][0] == 'chr5'
	assert hits[9]['start'][0] == 121
	assert hits[9]['end'][0] == 133
	assert hits[9]['strand'][0] == '+'
	assert round(hits[9]['score'][0], 4) == round(3.17477, 4)
	assert round(hits[9]['p-value'][0], 4) == round(0.000099, 4)


def test_fimo_pwm_dict():
	pwms = read_meme("tests/data/test.meme")
	hits = fimo(pwms, "tests/data/test.fa")

	assert len(hits) == 12
	for df in hits:
		assert isinstance(df, pandas.DataFrame)
		assert df.shape[1] == 8
		assert tuple(df.columns) == ('motif_name', 'motif_idx', 'sequence_name', 
			'start', 'end', 'strand', 'score', 'p-value')

	assert hits[0].shape == (1, 8)
	assert hits[9].shape == (1, 8)

	assert hits[0]['motif_name'][0] == "MEOX1_homeodomain_1"
	assert hits[0]['sequence_name'][0] == 'chr7'
	assert hits[0]['start'][0] == 1350
	assert hits[0]['end'][0] == 1360
	assert hits[0]['strand'][0] == '+'
	assert round(hits[0]['score'][0], 4) == round(11.446572, 4)
	assert round(hits[0]['p-value'][0], 4) == round(0.000075, 4)


	assert hits[9]['motif_name'][0] == "FOXQ1_MOUSE.H11MO.0.C"
	assert hits[9]['sequence_name'][0] == 'chr5'
	assert hits[9]['start'][0] == 121
	assert hits[9]['end'][0] == 133
	assert hits[9]['strand'][0] == '+'
	assert round(hits[9]['score'][0], 4) == round(3.17477, 4)
	assert round(hits[9]['p-value'][0], 4) == round(0.000099, 4)


'''
def test_fimo_pwm_torch():
	pwms = read_meme("tests/data/test.meme")
	pwms = {name: torch.from_numpy(pwm) for name, pwm in pwms.items()}
	hits = fimo(pwms, "tests/data/test.fa")

	assert len(hits) == 12
	for df in hits:
		assert isinstance(df, pandas.DataFrame)
		assert df.shape[1] == 8
		assert tuple(df.columns) == ('motif_name', 'motif_idx', 'sequence_name', 
			'start', 'end', 'strand', 'score', 'p-value')

	assert hits[0].shape == (1, 8)
	assert hits[9].shape == (1, 8)

	assert hits[0]['motif_name'][0] == "MEOX1_homeodomain_1"
	assert hits[0]['sequence_name'][0] == 'chr7'
	assert hits[0]['start'][0] == 1350
	assert hits[0]['end'][0] == 1360
	assert hits[0]['strand'][0] == '+'
	assert round(hits[0]['score'][0], 4) == round(11.446572, 4)
	assert round(hits[0]['p-value'][0], 4) == round(0.000075, 4)


	assert hits[9]['motif_name'][0] == "FOXQ1_MOUSE.H11MO.0.C"
	assert hits[9]['sequence_name'][0] == 'chr5'
	assert hits[9]['start'][0] == 121
	assert hits[9]['end'][0] == 133
	assert hits[9]['strand'][0] == '+'
	assert round(hits[9]['score'][0], 4) == round(3.17477, 4)
	assert round(hits[9]['p-value'][0], 4) == round(0.000099, 4)
'''


def test_fimo_bin_size():
	hits = fimo("tests/data/test.meme", "tests/data/test.fa", bin_size=1)

	assert len(hits) == 12
	for df in hits:
		assert isinstance(df, pandas.DataFrame)
		assert df.shape[1] == 8
		assert tuple(df.columns) == ('motif_name', 'motif_idx', 'sequence_name', 
			'start', 'end', 'strand', 'score', 'p-value')

	assert hits[0].shape == (0, 8)
	assert hits[9].shape == (1, 8)


	assert hits[9]['motif_name'][0] == "FOXQ1_MOUSE.H11MO.0.C"
	assert hits[9]['sequence_name'][0] == 'chr5'
	assert hits[9]['start'][0] == 121
	assert hits[9]['end'][0] == 133
	assert hits[9]['strand'][0] == '+'
	assert round(hits[9]['score'][0], 4) == round(3.17477, 4)
	assert round(hits[9]['p-value'][0], 4) == round(0.000099, 4)


def test_fimo_threshold():
	hits = fimo("tests/data/test.meme", "tests/data/test.fa", threshold=0.001)

	assert len(hits) == 12
	for df in hits:
		assert isinstance(df, pandas.DataFrame)
		assert df.shape[1] == 8
		assert tuple(df.columns) == ('motif_name', 'motif_idx', 'sequence_name', 
			'start', 'end', 'strand', 'score', 'p-value')

	assert hits[0].shape == (13, 8)
	assert hits[9].shape == (157, 8)

	assert_array_equal(hits[0]['sequence_name'].values, ['chr1', 'chr2',
		'chr7', 'chr7', 'chr7', 'chr7', 'chr7', 'chr7', 'chr7', 'chr7', 'chr7', 
		'chr7', 'chr7'])
	assert_array_equal(hits[0]['start'].values, [ 190, 183, 667, 1096, 1106, 
		1161, 1350, 1384,  393, 1096, 1106, 1161, 1350])
	assert_array_equal(hits[0]['end'].values, [ 200, 193,  677, 1106, 1116, 
		1171, 1360, 1394,  403, 1106, 1116, 1171, 1360])
	assert_array_equal(hits[0]['strand'].values, ['+', '+', '+', '+', '+', '+', 
		'+', '+', '-', '-', '-', '-', '-'])
	assert_array_almost_equal(hits[0]['score'].values, [ 7.83938732, 7.40117477,
		7.40117477, 10.07583028, 10.07583028, 10.07583028, 11.4465722, 
		9.66039708,  8.30576608,  7.42200964,  7.42200964,  7.42200964,
  		7.54405698], 4)
	assert_array_almost_equal(hits[0]['p-value'].values, [7.60078430e-04, 
		9.22203064e-04, 9.22203064e-04, 1.89781189e-04, 1.89781189e-04, 
		1.89781189e-04, 7.53402710e-05, 2.45094299e-04, 5.88417053e-04, 
		9.22203064e-04, 9.22203064e-04, 9.22203064e-04, 8.81195068e-04], 4)


def test_fimo_rc():
	hits = fimo("tests/data/test.meme", "tests/data/test.fa", 
		reverse_complement=False)

	assert len(hits[3]) == 1
	assert len(hits[7]) == 1
	assert len(hits[10]) == 1
