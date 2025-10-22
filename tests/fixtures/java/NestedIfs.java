/**
 * Test fixture: Nested if statements
 * Expected cognitive complexity: 6 (1 + 2 + 3)
 */
public class NestedIfs {
    public static boolean nestedIfs(boolean x, boolean y, boolean z) {
        if (x) {           // +1 (nesting level 0)
            if (y) {       // +2 (1 base + 1 nesting)
                if (z) {   // +3 (1 base + 2 nesting)
                    return true;
                }
            }
        }
        return false;
    }
}
