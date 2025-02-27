class Solution(object):
    def twoSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]

        index - x = target
        x = target - index
        x + index = target

        2: 1
        
        """
        index_mapper = {}
        index = 0
        while index < len(nums):
            ans = target - nums[index]
            if ans in index_mapper.keys():
                return [index_mapper.get(ans), index]
            index_mapper.update({nums[index]: index})
            index += 1


            
        return []
        

x = Solution()
ans = x.twoSum([6, 2, 9, 9, 2, 4, 1, 6, 4], 8)
print(ans)