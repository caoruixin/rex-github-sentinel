const { bubbleSort } = require('../code');

describe('bubbleSort', () => {
  test('sorts an array of numbers in ascending order', () => {
    const unsortedArray = [5, 3, 8, 2, 1, 9, 4, 7, 6];
    const sortedArray = bubbleSort(unsortedArray);
    expect(sortedArray).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9]);
  });

  test('handles an already sorted array', () => {
    const sortedArray = [1, 2, 3, 4, 5];
    const result = bubbleSort(sortedArray);
    expect(result).toEqual([1, 2, 3, 4, 5]);
  });

  test('sorts an array with duplicate elements', () => {
    const arrayWithDuplicates = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5];
    const sortedArray = bubbleSort(arrayWithDuplicates);
    expect(sortedArray).toEqual([1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9]);
  });

  test('handles an empty array', () => {
    const emptyArray = [];
    const result = bubbleSort(emptyArray);
    expect(result).toEqual([]);
  });

  test('sorts an array with negative numbers', () => {
    const arrayWithNegatives = [-3, 5, -1, 0, 2, -4];
    const sortedArray = bubbleSort(arrayWithNegatives);
    expect(sortedArray).toEqual([-4, -3, -1, 0, 2, 5]);
  });

  test('sorts an array with one element', () => {
    const singleElementArray = [42];
    const result = bubbleSort(singleElementArray);
    expect(result).toEqual([42]);
  });
});
