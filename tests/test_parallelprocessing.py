import time
import numpy
import pytest
from thread import ParallelProcessing, exceptions


# >>>>>>>>>> Dummy Functions <<<<<<<<<< #
def _dummy_dataProcessor(data_in: int, delay: float = 0) -> int:
  time.sleep(delay)
  return data_in

def _dummy_raiseException(x: Exception, delay: float = 0):
  time.sleep(delay)
  raise x




# >>>>>>>>>> General Use <<<<<<<<<< #
def test_threadsScaleDown():
  """This test is for testing if threads scale down `max_threads` when the dataset is lesser than the thread count"""
  dataset = numpy.arange(0, 2).tolist()
  new = ParallelProcessing(
    function = _dummy_dataProcessor,
    dataset = dataset,
    max_threads = 4,
    kwargs = { 'delay': 2 }
  )
  new.start()
  assert len(new._threads) == 2

def test_threadsProcessing():
  """This test is for testing if threads correctly order data in the `dataset` arrangement"""
  dataset = numpy.arange(0, 500).tolist()
  new = ParallelProcessing(
    function = _dummy_dataProcessor,
    dataset = dataset,
    args = [0.001]
  )
  new.start()
  assert new.get_return_values() == dataset




# >>>>>>>>>> Raising Exceptions <<<<<<<<<< #
def test_raises_notInitializedError():
  """This test should raise ThreadNotInitializedError"""
  dataset = numpy.arange(0, 8).tolist()
  new = ParallelProcessing(
    function = _dummy_dataProcessor,
    dataset = dataset
  )

  with pytest.raises(exceptions.ThreadNotInitializedError):
    new.results

def test_raises_StillRunningError():
  """This test should raise ThreadStillRunningError"""
  dataset = numpy.arange(0, 8).tolist()
  new = ParallelProcessing(
    function = _dummy_dataProcessor,
    dataset = dataset,
    args = [1]
  )
  new.start()
  with pytest.raises(exceptions.ThreadStillRunningError):
    new.results

def test_raises_RunTimeError():
  """This test should raise a RunTimeError"""
  dataset = [RuntimeError()] * 8
  new = ParallelProcessing(
    function = _dummy_raiseException,
    dataset = dataset,
    args = [0.01]
  )
  with pytest.raises(RuntimeError):
    new.start()
    new.join()