// Test fixture: Nested if statements
// Expected cognitive complexity: 6 (1 + 2 + 3)
package main

func nestedIfs(x, y, z bool) bool {
	if x { // +1 (nesting level 0)
		if y { // +2 (1 base + 1 nesting)
			if z { // +3 (1 base + 2 nesting)
				return true
			}
		}
	}
	return false
}
