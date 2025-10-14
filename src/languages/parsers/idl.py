import re
from src.languages.parsers.base import ComplexityParser


class IDLComplexityParser(ComplexityParser):
    """
    Complexity parser for IDL (Interface Definition Language) files.
    
    IDL is used to define interfaces between systems (CORBA, COM, etc.).
    Complexity metrics focus on:
    - Structural complexity (interfaces, structs, unions, exceptions)
    - Operation complexity (methods in interfaces)
    - Data complexity (nesting depth, sequences, arrays)
    - Inheritance and dependencies
    
    Example IDL:
        module MyModule {
            interface MyInterface {
                long operation1(in string param);
                void operation2();
            };
            
            struct MyStruct {
                long field1;
                string field2;
            };
        };
    """
    
    def compute_complexity(self, code: str) -> int:
        """
        Compute the structural complexity of the given IDL code.
        
        Complexity factors:
        - Interfaces: +3 each (define contracts)
        - Structs: +2 each (data structures)
        - Unions: +3 each (conditional data)
        - Exceptions: +2 each (error handling)
        - Operations/Methods: +2 each (behavior)
        - Enums: +1 each (simple types)
        - Typedefs: +1 each (aliases)
        - Inheritance (extends): +2 each (dependency)
        - Attributes: +1 each (state)
        - Nesting depth: +2 per level beyond 1
        - Sequences/Arrays: +1 each (collection types)
        
        Args:
            code: IDL source code as string
            
        Returns:
            Integer representing structural complexity
        """
        complexity = 1  # Base complexity
        
        # Remove comments to avoid false matches
        code = self._remove_comments(code)
        
        # Count major structural elements
        complexity += len(re.findall(r'\binterface\s+\w+', code)) * 3
        complexity += len(re.findall(r'\bstruct\s+\w+', code)) * 2
        complexity += len(re.findall(r'\bunion\s+\w+', code)) * 3
        complexity += len(re.findall(r'\bexception\s+\w+', code)) * 2
        complexity += len(re.findall(r'\benum\s+\w+', code)) * 1
        complexity += len(re.findall(r'\btypedef\s+', code)) * 1
        
        # Count operations (methods) in interfaces
        # Pattern: return_type method_name(params) [raises (...)];
        # Return type can include <> for sequences, e.g., sequence<Type>
        # Operations may have 'raises' clause before semicolon
        operations = re.findall(r'\b[\w<>]+\s+\w+\s*\([^)]*\)(?:\s+raises\s*\([^)]*\))?\s*;', code)
        complexity += len(operations) * 2
        
        # Count attributes (state in interfaces)
        attributes = re.findall(r'\battribute\s+\w+\s+\w+', code)
        complexity += len(attributes)
        
        # Count inheritance relationships
        complexity += len(re.findall(r'\bextends\s+\w+', code)) * 2
        # C++ style inheritance (interface Foo : Bar) - not case labels
        # Must be preceded by interface/struct name, not case/default
        complexity += len(re.findall(r'(?:interface|struct|exception)\s+\w+\s*:\s*\w+', code)) * 2
        
        # Count sequences and arrays (collection types)
        complexity += len(re.findall(r'\bsequence\s*<', code))
        complexity += len(re.findall(r'\w+\s+\w+\[\s*\d*\s*\]', code))
        
        # Calculate nesting depth (modules, interfaces, structs)
        nesting_depth = self._calculate_nesting_depth(code)
        if nesting_depth > 1:
            complexity += (nesting_depth - 1) * 2
        
        return complexity
    
    def _remove_comments(self, code: str) -> str:
        """
        Remove C-style comments (// and /* */) from IDL code.
        """
        # Remove single-line comments
        code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
        # Remove multi-line comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code
    
    def _calculate_nesting_depth(self, code: str) -> int:
        """
        Calculate maximum nesting depth of braces { }.
        IDL uses braces for modules, interfaces, structs, unions, etc.
        """
        max_depth = 0
        current_depth = 0
        
        for char in code:
            if char == '{':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == '}':
                current_depth = max(0, current_depth - 1)
        
        return max_depth
    
    def count_functions(self, code: str) -> int:
        """
        Count operations (methods) defined in IDL interfaces.
        
        Returns:
            Number of operations/methods
        """
        code = self._remove_comments(code)
        operations = re.findall(r'\b\w+\s+\w+\s*\([^)]*\)\s*;', code)
        return len(operations)
    
    def analyze_functions(self, code: str) -> list[dict[str, any]]:
        """
        Analyze individual operations (methods) in IDL interfaces.
        
        Returns:
            List of dicts with 'name' and 'complexity' for each operation
        """
        functions = []
        code = self._remove_comments(code)
        
        # Pattern to match operations: return_type method_name(params);
        pattern = r'\b\w+\s+(\w+)\s*\(([^)]*)\)\s*;'
        matches = re.finditer(pattern, code)
        
        for match in matches:
            method_name = match.group(1)
            params = match.group(2)
            
            # Simple complexity: 1 base + 1 per parameter
            param_count = 0
            if params.strip():
                # Count parameters by splitting on commas
                param_count = len([p for p in params.split(',') if p.strip()])
            
            method_complexity = 1 + param_count
            
            functions.append({
                'name': method_name,
                'complexity': method_complexity
            })
        
        return functions
    
    # Pattern for matching function/operation definitions
    # Used by base class if needed
    FUNCTION_PATTERN = r'\b\w+\s+(\w+)\s*\([^)]*\)\s*;'
