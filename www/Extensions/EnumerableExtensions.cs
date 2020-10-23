using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace cc.net.Extensions
{
    public static class EnumerableExtensions
    {
        public static IEnumerable<IEnumerable<T>> CartesianProduct<T> (this IEnumerable<IEnumerable<T>> sequences)
        {
            IEnumerable<IEnumerable<T>> emptyProduct = new[] { Enumerable.Empty<T>() };
            IEnumerable<IEnumerable<T>> result = emptyProduct;
            foreach (IEnumerable<T> sequence in sequences)
            {
                result = from accseq in result from item in sequence select accseq.Concat(new[] { item });
            }
            return result;
        }
    }

    public static class CrossProductFunctions
    {


        /// <summary>
        /// Gets a multiple-cross-product of all of the numbers from [0,0,0] to [i1, i2, ...]
        /// </summary>
        /// <param name="maxIndices">A list of the maximum indices to iterate in each position (eg [2,4,1]</param>
        /// <returns>An iterator of cross-products ([0,0,0], [0,0,1], [0,1,0], etc)</returns>
        public static IEnumerable<List<int>> IndexCrossProduct(List<int> maxIndices)
        {
            //don't do anything to an empty lsit
            if (maxIndices == null || maxIndices.Count == 0)
                yield break;

            //we repeatedly make reference to what's the index of the last digit in the enumeration
            var lastIndex = maxIndices.Count - 1;

            //initialize the iterable return value. Start with [0,0,0, etc]
            List<int> currentIndices = Enumerable.Repeat(0, maxIndices.Count).ToList();

            //increment the iteration by repeatedly adding one to the next index.
            for (; true; currentIndices[lastIndex]++)
            {
                //This could result in a value for the last place outside of the allowed range.
                //If so, we repeately "carry" the value over to the previous index, in a fasion similar to adding 1 to 099

                //for reach index in the set, working right to left
                for (int incrementIndex = lastIndex; true; incrementIndex--)
                {
                    //if no overflow, we can directly return the enumerator value
                    if (currentIndices[incrementIndex] <= maxIndices[incrementIndex])
                    {
                        yield return currentIndices.Select(i => i).ToList(); //copy the list
                        break;
                    }

                    //If addition would completely break range, exit
                    if (incrementIndex == 0)
                        yield break;

                    //else, carry the increment to the next index
                    currentIndices[incrementIndex] = 0;
                    currentIndices[incrementIndex - 1]++;
                }




            }

        }

        /// <summary>
        /// Finds the multi-cross-product of an list of object lists
        /// </summary>
        /// <typeparam name="T">The type of the object being enumerated</typeparam>
        /// <param name="possibleValueArrays">The list of object lists to cross-product over</param>
        /// <returns>An iterator of the cross products</returns>
        public static IEnumerable<List<T>> CrossProduct<T>(this List<List<T>> possibleValueArrays)
        {


            //The technique is to iterate over the possible index values, then use each generated
            //integer cross product as indices for the possibleValueArrays
            var maxIndices = possibleValueArrays.Select(arr => arr.Count - 1).ToList();

            //convert each generated possible index to the underlying values
            foreach (var indexList in IndexCrossProduct(maxIndices))
            {
                yield return possibleValueArrays.Select((values, i) => values[indexList[i]]).ToList();

            }
            yield break;
        }

    }
}
