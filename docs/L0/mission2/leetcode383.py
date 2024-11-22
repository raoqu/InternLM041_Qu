class Solution:
    def canConstruct(self, ransomNote: str, magazine: str) -> bool:
        chcount = {}

        for ch in magazine:
            if ch in chcount:
                chcount[ch] = chcount[ch] + 1
            else:
                chcount[ch] = 1
        
        for ch in ransomNote:
            if ch not in chcount or chcount[ch] < 1:
                return False
            chcount[ch] = chcount[ch] - 1
        
        return True

solution = Solution()
cases = [
    ["a", "b"],
    ["aa", "ab"],
    ["aa", "aab"],
    ["abaabc", "aabbabcc"]
    ]
for thecase in cases:
    ransomNote, magazine = thecase
    result = solution.canConstruct(ransomNote, magazine)
    print(ransomNote, magazine, '->', result)
