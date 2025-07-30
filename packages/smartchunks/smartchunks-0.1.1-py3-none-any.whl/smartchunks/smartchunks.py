from typing import Iterable, Generator, TypeVar, List, Optional, Callable, Union

T = TypeVar('T')

def chunked(
    iterable: Iterable[T],
    size: int,
    nth_position: Optional[int] = None,
    chunk_position: Optional[int] = None,
    apply_nth_before_chunk: bool = True,
    stride: Optional[int] = None,
    fillvalue: Optional[T] = None,
    filter_fn: Optional[Callable[[List[T]], bool]] = None,
    materialize: bool = False
) -> Union[Generator[List[T], None, None], List[List[T]]]:
    if size <= 0:
        raise ValueError("Chunk size must be > 0")

    data = list(iterable)

    # Step 1: Apply nth_position before chunking if specified
    if apply_nth_before_chunk and nth_position:
        data = data[::nth_position]

    # Step 2: Calculate stride-based or regular chunks
    step = stride if stride else size
    chunks = [data[i:i + size] for i in range(0, len(data), step)]
    if fillvalue is not None and chunks and len(chunks[-1]) < size:
        chunks[-1] += [fillvalue] * (size - len(chunks[-1]))

    # Step 3: Filter chunks by chunk_position if specified
    if chunk_position:
        chunks = [chunk for i, chunk in enumerate(chunks, start=1) if i % chunk_position == 0]

    # Step 4: Apply nth_position after chunking (if not already applied)
    if not apply_nth_before_chunk and nth_position:
        chunks = [[chunk[nth_position - 1]] for chunk in chunks if len(chunk) >= nth_position]

    # Step 5: Apply filter function
    if filter_fn:
        chunks = list(filter(filter_fn, chunks))

    return chunks if materialize else iter(chunks)

