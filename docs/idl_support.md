# IDL (Interface Definition Language) Support in MetricMancer

## Overview

MetricMancer provides comprehensive complexity analysis for IDL (Interface Definition Language) files. IDL is commonly used in middleware systems like CORBA, COM/DCOM, and other distributed computing frameworks to define interfaces between system components.

## Features

### ✅ Structural Complexity Analysis

The IDL parser analyzes the structural complexity of interface definitions, measuring:

- **Interfaces** (+3 each): Primary contracts that define service APIs
- **Structs** (+2 each): Data structures for parameter and return types
- **Unions** (+3 each): Conditional data types (discriminated unions)
- **Exceptions** (+2 each): Error handling definitions
- **Operations** (+2 each): Methods defined in interfaces
- **Enums** (+1 each): Simple enumeration types
- **Typedefs** (+1 each): Type aliases
- **Attributes** (+1 each): State variables in interfaces
- **Inheritance** (+2 each): Interface extension relationships
- **Nesting Depth** (+2 per level beyond 1): Module and interface nesting
- **Collections** (+1 each): Sequences and arrays

### ✅ Operation Analysis

- Counts all operations (methods) defined in interfaces
- Analyzes individual operations with parameter complexity
- Handles `raises` clauses for exception specifications
- Supports complex return types including sequences

### ✅ Full Integration

IDL files receive the same comprehensive analysis as other supported languages:

- **Code Churn**: Git history analysis to identify frequently changed interfaces
- **Hotspot Detection**: Complexity × Churn identifies high-risk interface definitions
- **Ownership Analysis**: Git blame analysis shows who maintains which interfaces
- **Review Strategy**: Data-driven recommendations for interface reviews

## Complexity Calculation

### Base Formula

```
Complexity = 1 (base)
           + (interfaces × 3)
           + (structs × 2)
           + (unions × 3)
           + (exceptions × 2)
           + (operations × 2)
           + (enums × 1)
           + (typedefs × 1)
           + (attributes × 1)
           + (inheritance × 2)
           + (sequences/arrays × 1)
           + (nesting_depth - 1) × 2
```

### Example Calculation

```idl
module Banking {                          // +2 nesting depth (level 2)
    exception InsufficientFunds {         // +2 exception
        string message;
        long accountId;
    };
    
    struct Account {                      // +2 struct
        long id;
        string owner;
        double balance;
    };
    
    interface BankService {               // +3 interface
        Account getAccount(in long id);   // +2 operation
        void deposit(in long id, in double amount);     // +2 operation
        void withdraw(in long id, in double amount)     // +2 operation
            raises (InsufficientFunds);
        sequence<Account> listAccounts(); // +2 operation, +1 sequence
    };
};

Total Complexity = 1 + 2 + 2 + 3 + 8 + 1 + 2 = 19
```

## Usage Examples

### Basic Analysis

```bash
# Analyze a directory containing IDL files
python -m src.main path/to/idl/files

# Generate review strategy for IDL interfaces
python -m src.main path/to/idl --review-strategy
```

### Review Strategy Output

```
File: BankingService.idl
   Complexity: 19       ← Structural complexity
   Churn: 5.0          ← Number of commits affecting this file
   Hotspot: 95         ← 19 × 5 = 95
   Ownership: Single   ← One primary maintainer
   
   Risk Level: MEDIUM
   Estimated Review Time: 45 minutes
   
   Review Focus:
   ✓ Interface compatibility and versioning
   ✓ Operation signature changes (breaking changes)
   ✓ Exception handling completeness
   ✓ Data structure evolution
   ✓ Inheritance hierarchy complexity
```

## Supported IDL Features

### ✅ Fully Supported

- **Modules**: Nested namespaces
- **Interfaces**: With operations, attributes, and inheritance
- **Data Types**: struct, union, enum, sequence, array
- **Exceptions**: Exception definitions and raises clauses
- **Type Definitions**: typedef aliases
- **Inheritance**: Single and multiple interface inheritance
- **Operations**: Methods with parameters and return types
- **Attributes**: State variables in interfaces
- **Comments**: C-style single-line (//) and multi-line (/* */)

### 📋 Common IDL Patterns

**CORBA Style:**
```idl
module CosNaming {
    interface NamingContext {
        void bind(in Name n, in Object obj);
        Object resolve(in Name n);
    };
};
```

**COM/DCOM Style:**
```idl
interface IUnknown {
    HRESULT QueryInterface([in] REFIID riid, [out] void** ppv);
    ULONG AddRef();
    ULONG Release();
};
```

## Integration with Review Strategy

### Risk Classification

IDL files are classified using the same risk levels as code files:

- **Critical**: High complexity (15+) + High churn (6+)
- **High**: Moderate-high complexity (11-15) or High churn
- **Medium**: Moderate complexity (6-10) or Moderate churn
- **Low**: Low complexity (1-5) and Low churn (0-2)

### Review Checklists

Based on complexity and churn, the system generates targeted review checklists:

**High Complexity Interface:**
- [ ] Verify interface compatibility and versioning strategy
- [ ] Check for breaking changes in operation signatures
- [ ] Review exception handling completeness
- [ ] Validate parameter and return type choices
- [ ] Consider interface splitting for better maintainability

**High Churn Interface:**
- [ ] Document reason for frequent changes
- [ ] Review change history for patterns
- [ ] Consider interface stability and maturity
- [ ] Check for backwards compatibility
- [ ] Update documentation and examples

**Inheritance Complexity:**
- [ ] Review inheritance hierarchy depth
- [ ] Check for diamond inheritance problems
- [ ] Validate interface segregation principle
- [ ] Consider composition over inheritance

## Use Cases

### 1. Interface Evolution Analysis

Track how interfaces change over time:
```bash
python -m src.main idl/ --list-hotspots --hotspot-threshold 50
```

### 2. Code Review Prioritization

Focus reviews on high-risk interfaces:
```bash
python -m src.main idl/ --review-strategy --review-branch-only
```

### 3. Maintenance Planning

Identify complex interfaces that need refactoring:
```bash
python -m src.main idl/ --output-format json --hierarchical
```

### 4. Team Onboarding

Help new developers understand interface complexity:
```bash
python -m src.main idl/ --output-format html
```

## Testing

The IDL parser includes comprehensive test coverage:

- **19 unit tests** covering all complexity scenarios
- Tests for interfaces, structs, unions, exceptions
- Inheritance and nesting depth tests
- Operation counting and analysis
- Comment handling validation
- Real-world CORBA example tests

Run tests:
```bash
pytest tests/languages/test_idl_parser.py -v
```

## Technical Details

### Parser Implementation

**Location**: `src/languages/parsers/idl.py`

**Key Components**:
- `IDLComplexityParser`: Main parser class
- `compute_complexity()`: Calculates structural complexity
- `count_functions()`: Counts operations in interfaces
- `analyze_functions()`: Analyzes individual operations
- `_calculate_nesting_depth()`: Measures module/interface nesting
- `_remove_comments()`: Cleans C-style comments

### Configuration

**Location**: `src/languages/config.py`

```python
'.idl': {
    'name': 'IDL',
    'parser': 'IDLComplexityParser'
}
```

## Best Practices

### For IDL Authors

1. **Keep interfaces focused**: High operation count increases complexity
2. **Limit inheritance depth**: Deep hierarchies are harder to maintain
3. **Document complex types**: Unions and nested structures need clear docs
4. **Version interfaces carefully**: Breaking changes impact all clients

### For Reviewers

1. **Check backwards compatibility**: Interface changes affect all consumers
2. **Verify exception specifications**: Ensure complete error handling
3. **Review parameter choices**: In/out/inout semantics must be correct
4. **Consider performance**: Complex types may impact marshalling

### For Teams

1. **Monitor hotspots**: Frequently changed interfaces need attention
2. **Track ownership**: Ensure knowledge distribution
3. **Use review strategy**: Prioritize reviews based on data
4. **Document patterns**: Establish interface design guidelines

## Limitations

### Not Analyzed

- **Semantic correctness**: Parser doesn't validate IDL semantics
- **Cross-reference complexity**: Dependencies between interfaces not tracked
- **Performance implications**: Marshalling costs not considered
- **Platform-specific features**: OMG IDL, Microsoft IDL differences

### Future Enhancements

- Cross-file interface dependency analysis
- Breaking change detection across versions
- IDL-to-language binding complexity
- Performance impact estimation

## Resources

- **CORBA IDL Specification**: [OMG IDL Syntax and Semantics](https://www.omg.org/spec/IDL/)
- **Microsoft IDL**: [MIDL Language Reference](https://docs.microsoft.com/en-us/windows/win32/midl/midl-language-reference)
- **Parser Documentation**: `src/languages/parsers/idl.py`
- **Test Examples**: `tests/languages/test_idl_parser.py`

## Contributing

To extend IDL support:

1. Add new complexity factors in `compute_complexity()`
2. Update test suite in `tests/languages/test_idl_parser.py`
3. Document changes in this file
4. Run full test suite: `pytest tests/ -v`

---

**Last Updated**: October 13, 2025  
**MetricMancer Version**: 2.1.0 (Unreleased)  
**Maintainer**: CmdrPrompt
