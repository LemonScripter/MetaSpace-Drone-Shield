# Contributing to MetaSpace-Drone-Shield

Thank you for your interest in contributing to MetaSpace-Drone-Shield! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and professional
- Focus on technical merit
- Maintain scientific rigor
- No marketing hype or false promises

## How to Contribute

### 1. Report Issues

If you find a bug or have a suggestion, please open an issue with:

**Title Format:** `[BUG]` or `[FEATURE]` or `[DOCS]` - Brief description

**Issue Template:**
```
**Environment:**
- Hardware: (e.g., Pixhawk 4 Mini, ArduCopter 4.5)
- Software: (e.g., Python 3.9, Z3 4.8)
- OS: (e.g., Ubuntu 20.04)

**Description:**
Clear description of the issue or feature request

**Reproduction Steps:**
1. Step 1
2. Step 2
3. ...

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Additional Context:**
Any other relevant information
```

### 2. Submit Pull Requests

**Workflow:**
```bash
# 1. Fork the repository
# 2. Create a feature branch
git checkout -b feature/your-feature-name

# 3. Make your changes
# 4. Write/update tests
# 5. Commit with clear messages
git commit -m "feat: Add feature X"
git commit -m "fix: Fix bug Y"
git commit -m "docs: Update documentation"

# 6. Push to your fork
git push origin feature/your-feature-name

# 7. Open a Pull Request
```

**Pull Request Template:**
- Clear description of changes
- Reference to related issues
- Test results (if applicable)
- Documentation updates (if needed)

### 3. Code Style

#### Python
- Follow PEP 8
- Use Black formatter (line length: 100)
- Type hints for function signatures
- Docstrings for all public functions/classes

**Example:**
```python
def check_gps_measurement(
    gps_loc: Location,
    velocity: Vector3f,
    acceleration: Vector3f
) -> bool:
    """
    Check GPS measurement against kinematic invariants.
    
    Args:
        gps_loc: GPS position measurement
        velocity: IMU-derived velocity
        acceleration: IMU-derived acceleration
    
    Returns:
        True if spoofing detected, False otherwise
    """
    # Implementation
    pass
```

#### C++
- Follow Google C++ Style Guide
- Use clang-format
- Document all public APIs

#### Comments
- **English only** (no Hungarian)
- Technical, precise, engineering-focused
- Explain "why" not just "what"

### 4. Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: Add new feature
fix: Fix bug
docs: Update documentation
test: Add or update tests
refactor: Code refactoring
perf: Performance improvement
chore: Maintenance tasks
```

**Examples:**
```
feat: Add covert spoofing detection
fix: Fix Z3 solver timeout on Pixhawk
docs: Update LIMITATIONS.md with sensor calibration info
test: Add test for AF447 scenario
```

### 5. Testing

**Required:**
- Unit tests for new functions
- Integration tests for new features
- Update existing tests if behavior changes

**Run Tests:**
```bash
# Python tests
pytest validation/ -v

# C++ tests (when implemented)
cd build && make test
```

### 6. Documentation

**Required Updates:**
- README.md (if user-facing changes)
- docs/ARCHITECTURE.md (if architecture changes)
- docs/LIMITATIONS.md (if limitations change)
- Code comments (for new code)

**Documentation Style:**
- Clear, technical, precise
- No marketing language
- State limitations transparently
- Use examples where helpful

## Development Workflow

### Phase 1: Simulation Development
```bash
cd validation/gazebo_tests
python test_scenario_1_overt_spoofing.py
```

### Phase 2: Hardware Testing
```bash
cd validation/hardware_tests
python sitl_validation_tool.py
```

### Phase 3: Analysis
```bash
cd src/python/analysis
python invariant_checker.py
```

## Security & Sensitive Files

**Important:** Never commit sensitive files:
- Proprietary core modules
- Classified specifications
- API keys or credentials
- Personal information

**Hash Verification:**
- Sensitive files are protected via SHA-256 hashes
- See `PROTECTED_FILES_LIST.md` for hash verification
- See `.gitignore` for excluded patterns

## Questions?

- Open an issue for questions
- Check existing documentation first
- Be specific about what you need help with

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md (when created)
- Release notes
- Project documentation

Thank you for contributing to MetaSpace-Drone-Shield!

