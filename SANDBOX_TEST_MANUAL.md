ls -la /tmp/pakagent_sandbox/
tree /tmp/pakagent_sandbox/# 🧪 PakAgent Sandbox - Manual Test Instructions

## 📁 Sandbox Overview

**Location:** `/tmp/pakagent_sandbox/`

**Sample Programs:**

- `src/web_server.py` - Simple HTTP server with API endpoints
- `src/data_processor.py` - CSV data processing and statistics

## 🚀 Quick Setup & Test

### 1. Verify Sandbox Content

bash. Test Sample Programs

**Test Web Server:**

```bash
cd /tmp/pakagent_sandbox
python src/web_server.py &
# Server starts on port 8080

# Test endpoints
curl http://localhost:8080/
curl http://localhost:8080/api/status
curl http://localhost:8080/api/time

# Stop server
pkill -f web_server.py
```

**Test Data Processor:**

```bash
cd /tmp/pakagent_sandbox
python src/data_processor.py

# Check generated files
cat config/sample_data.csv
cat config/report.json
```

## 🔬 PakDiff Workflow Test

### 3. Run PakAgent on Sandbox

```bash
# Set sandbox as target
export PAK_SOURCE_DIR=/tmp/pakagent_sandbox

# Start pakdiff workflow from pakagent directory
cd /home/pakkio/IdeaProjects/pakagent
poetry run python main_launcher.py
```

### 4. Manual Test Scenarios

**Scenario A: Add Error Handling**

- Wait for LLM to generate pakdiff for error handling
- Preview the suggested changes
- Apply if reasonable (press 'a')
- Verify the changes work correctly

**Scenario B: Add Logging**

- Wait for logging enhancement suggestions
- Preview the pakdiff format changes
- Test apply/skip/delete options

**Scenario C: Performance Improvements**

- Look for caching or optimization suggestions
- Review surgical method modifications
- Apply and test functionality

### 5. Verification Steps

**After Each Applied Change:**

```bash
# Test web server still works
python /tmp/pakagent_sandbox/src/web_server.py &
curl http://localhost:8080/api/status
pkill -f web_server.py

# Test data processor still works
python /tmp/pakagent_sandbox/src/data_processor.py
```

**Check Applied Changes:**

```bash
# View modified files
cat /tmp/pakagent_sandbox/src/web_server.py
cat /tmp/pakagent_sandbox/src/data_processor.py

# Check pakdiff archive
ls /tmp/pak_workflow_*/applied/
ls /tmp/pak_workflow_*/failed/
```

## 🎯 Surgical Modification Examples

**Expected PakDiff Targets:**

- `def send_status()` - Add error handling
- `def calculate_statistics()` - Add input validation
- `def load_csv()` - Add logging
- `def start_server()` - Add configuration options
- `def process_all_data()` - Add progress reporting

## ✅ Success Criteria

1. **LLM Generates Valid PakDiffs** - Syntax verified with `pak -vd`
2. **Surgical Application Works** - Only targeted methods modified
3. **Programs Still Function** - No breaking changes
4. **Changes Make Sense** - Logical improvements applied
5. **Preview System Works** - Can review before applying
6. **Archive System Works** - Applied changes tracked

## 🔧 Troubleshooting

**If LLM doesn't generate changes:**

- Check `OPENROUTER_API_KEY` in `.env`
- Verify API credits/limits
- Check network connectivity

**If pakdiff application fails:**

- Run `pak -vd changes.diff` to verify syntax
- Check file permissions
- Ensure pak v5.0.0 is installed

**If programs break after changes:**

- Check `/tmp/pak_workflow_*/applied/` for applied changes
- Restore from git or backup
- Review pakdiff content for syntax errors

## 📊 Expected Results

**Typical LLM Enhancements:**

- Error handling in web endpoints
- Input validation in data methods
- Logging for debugging
- Configuration parameters
- Documentation improvements
- Performance optimizations

The sandbox provides a safe, controlled environment to test the **pakdiff surgical modification workflow** with realistic Python programs!
