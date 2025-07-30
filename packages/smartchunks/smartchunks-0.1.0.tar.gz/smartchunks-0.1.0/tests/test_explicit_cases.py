
from smartchunks import chunked

def test_chunk_every_2nd_element():
    result = list(chunked([1,2,3,4,5,6,7,8,9], size=2, nth_position=2))
    assert result == [[1, 3], [5, 7], [9]]

def test_filter_sum_gt_15_with_stride():
    result = list(chunked([1,2,3,4,5,6,7,8,9], size=3, stride=1, filter_fn=lambda x: sum(x) > 15))
    assert result == [[5, 6, 7], [6, 7, 8], [7, 8, 9], [8, 9]]
