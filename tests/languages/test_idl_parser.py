"""
Unit tests for IDL (Interface Definition Language) complexity parser.
Tests structural complexity calculation, operation counting, and function analysis.
"""
import unittest
from src.languages.parsers.idl import IDLComplexityParser


class TestIDLComplexityParser(unittest.TestCase):
    """Test cases for IDL complexity parser."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = IDLComplexityParser()

    def test_empty_file(self):
        """Test that empty IDL file has base complexity of 1."""
        code = ""
        complexity = self.parser.compute_complexity(code)
        self.assertEqual(complexity, 1)

    def test_simple_interface(self):
        """Test complexity of a simple interface with operations."""
        code = """
        module MyModule {
            interface MyInterface {
                long getValue();
                void setValue(in long value);
            };
        };
        """
        complexity = self.parser.compute_complexity(code)
        # 1 base + 3 (interface) + 4 (2 operations * 2) + 2 (nesting depth 2)
        self.assertEqual(complexity, 10)

    def test_struct_definition(self):
        """Test complexity of struct definitions."""
        code = """
        struct Person {
            string name;
            long age;
            string email;
        };
        """
        complexity = self.parser.compute_complexity(code)
        # 1 base + 2 (struct)
        self.assertEqual(complexity, 3)

    def test_union_definition(self):
        """Test complexity of union definitions."""
        code = """
        union Data switch (long) {
            case 1: long intValue;
            case 2: string stringValue;
            default: boolean boolValue;
        };
        """
        complexity = self.parser.compute_complexity(code)
        # 1 base + 3 (union)
        self.assertEqual(complexity, 4)

    def test_exception_definition(self):
        """Test complexity of exception definitions."""
        code = """
        exception InvalidArgument {
            string message;
            long errorCode;
        };
        """
        complexity = self.parser.compute_complexity(code)
        # 1 base + 2 (exception)
        self.assertEqual(complexity, 3)

    def test_enum_definition(self):
        """Test complexity of enum definitions."""
        code = """
        enum Color {
            RED,
            GREEN,
            BLUE
        };
        """
        complexity = self.parser.compute_complexity(code)
        # 1 base + 1 (enum)
        self.assertEqual(complexity, 2)

    def test_typedef_definition(self):
        """Test complexity of typedef aliases."""
        code = """
        typedef long UserId;
        typedef string UserName;
        """
        complexity = self.parser.compute_complexity(code)
        # 1 base + 2 (2 typedefs)
        self.assertEqual(complexity, 3)

    def test_interface_with_inheritance(self):
        """Test complexity with interface inheritance."""
        code = """
        interface BaseInterface {
            void baseMethod();
        };

        interface DerivedInterface extends BaseInterface {
            void derivedMethod();
        };
        """
        complexity = self.parser.compute_complexity(code)
        # 1 base + 6 (2 interfaces * 3) + 4 (2 operations * 2) + 2 (extends)
        self.assertEqual(complexity, 13)

    def test_interface_with_attributes(self):
        """Test complexity with interface attributes."""
        code = """
        interface MyInterface {
            attribute string name;
            attribute long count;
            void doSomething();
        };
        """
        complexity = self.parser.compute_complexity(code)
        # 1 base + 3 (interface) + 2 (1 operation * 2) + 2 (2 attributes)
        self.assertEqual(complexity, 8)

    def test_sequences_and_arrays(self):
        """Test complexity with sequences and arrays."""
        code = """
        struct Container {
            sequence<long> numbers;
            string names[10];
            sequence<string> descriptions;
        };
        """
        complexity = self.parser.compute_complexity(code)
        # 1 base + 2 (struct) + 2 (2 sequences) + 1 (1 array)
        self.assertEqual(complexity, 6)

    def test_nested_modules(self):
        """Test complexity with nested module structure."""
        code = """
        module OuterModule {
            module InnerModule {
                interface MyInterface {
                    void operation();
                };
            };
        };
        """
        complexity = self.parser.compute_complexity(code)
        # 1 base + 3 (interface) + 2 (1 operation * 2) + 4 (nesting depth 3, (3-1)*2)
        self.assertEqual(complexity, 10)

    def test_complex_interface(self):
        """Test complexity of a comprehensive IDL interface."""
        code = """
        module Banking {
            exception InsufficientFunds {
                string message;
                long accountId;
            };

            struct Account {
                long id;
                string owner;
                double balance;
            };

            interface BankService {
                Account getAccount(in long accountId);
                void deposit(in long accountId, in double amount);
                void withdraw(in long accountId, in double amount) raises (InsufficientFunds);
                sequence<Account> listAccounts();
            };
        };
        """
        complexity = self.parser.compute_complexity(code)
        # 1 base + 2 (exception) + 2 (struct) + 3 (interface)
        # + 8 (4 operations * 2) + 1 (sequence) + 2 (nesting depth 2)
        self.assertEqual(complexity, 19)

    def test_comments_ignored(self):
        """Test that comments are ignored in complexity calculation."""
        code = """
        // This is a single-line comment
        /* This is a
           multi-line comment */
        interface MyInterface {
            // Comment before operation
            void operation(); // Inline comment
            /* Block comment
               spanning multiple lines */
        };
        """
        complexity = self.parser.compute_complexity(code)
        # 1 base + 3 (interface) + 2 (1 operation * 2)
        self.assertEqual(complexity, 6)

    def test_count_functions_simple(self):
        """Test counting operations in a simple interface."""
        code = """
        interface MyInterface {
            void operation1();
            long operation2(in string param);
            void operation3(in long a, in long b);
        };
        """
        count = self.parser.count_functions(code)
        self.assertEqual(count, 3)

    def test_count_functions_empty(self):
        """Test counting operations in empty interface."""
        code = """
        interface EmptyInterface {
        };
        """
        count = self.parser.count_functions(code)
        self.assertEqual(count, 0)

    def test_analyze_functions(self):
        """Test analyzing individual operations."""
        code = """
        interface Calculator {
            long add(in long a, in long b);
            long subtract(in long a, in long b);
            void reset();
        };
        """
        functions = self.parser.analyze_functions(code)

        self.assertEqual(len(functions), 3)

        # Check function names
        function_names = [f['name'] for f in functions]
        self.assertIn('add', function_names)
        self.assertIn('subtract', function_names)
        self.assertIn('reset', function_names)

        # Check complexities (1 base + param count)
        add_func = next(f for f in functions if f['name'] == 'add')
        self.assertEqual(add_func['complexity'], 3)  # 1 + 2 params

        subtract_func = next(f for f in functions if f['name'] == 'subtract')
        self.assertEqual(subtract_func['complexity'], 3)  # 1 + 2 params

        reset_func = next(f for f in functions if f['name'] == 'reset')
        self.assertEqual(reset_func['complexity'], 1)  # 1 + 0 params

    def test_nesting_depth_calculation(self):
        """Test nesting depth calculation."""
        code = """
        module Level1 {
            module Level2 {
                module Level3 {
                    interface MyInterface {
                    };
                };
            };
        };
        """
        complexity = self.parser.compute_complexity(code)
        # 1 base + 3 (interface) + 6 (nesting depth 4, (4-1)*2)
        self.assertEqual(complexity, 10)

    def test_multiple_inheritance(self):
        """Test complexity with multiple inheritance relationships."""
        code = """
        interface Base1 { };
        interface Base2 { };

        interface Derived extends Base1, Base2 {
            void operation();
        };
        """
        # Note: The parser counts 'extends Base1' once, not per base
        complexity = self.parser.compute_complexity(code)
        # 1 base + 9 (3 interfaces * 3) + 2 (1 operation * 2) + 2 (extends)
        self.assertEqual(complexity, 14)

    def test_real_world_corba_example(self):
        """Test with a realistic CORBA IDL example."""
        code = """
        module CosNaming {
            typedef string Istring;

            struct NameComponent {
                Istring id;
                Istring kind;
            };

            typedef sequence<NameComponent> Name;

            enum BindingType {
                nobject,
                ncontext
            };

            struct Binding {
                Name binding_name;
                BindingType binding_type;
            };

            interface NamingContext {
                void bind(in Name n, in Object obj);
                void rebind(in Name n, in Object obj);
                void unbind(in Name n);
                Object resolve(in Name n);
            };
        };
        """
        complexity = self.parser.compute_complexity(code)
        # 1 base + 2 (typedef *2) + 2 (struct) + 1 (enum) + 2 (struct)
        # + 3 (interface) + 8 (4 operations * 2) + 1 (sequence) + 2 (nesting depth 2)
        self.assertEqual(complexity, 22)


if __name__ == '__main__':
    unittest.main()
