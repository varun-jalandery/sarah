# Dynamic Distance Filtering Guide

## Overview

Dynamic Distance Filtering is an advanced feature in MyAI that improves the accuracy of document retrieval by filtering ChromaDB query results based on semantic similarity distances. This helps reduce noise and ensures only the most relevant documents are used for generating responses.

## How It Works

The system implements multiple filtering strategies that work together:

### 1. Base Threshold Filtering
- Removes results beyond a fixed distance threshold
- Configurable via `BASE_DISTANCE_THRESHOLD` (default: 0.8)
- Acts as a hard limit for maximum allowed distance

### 2. Dynamic Ratio Filtering  
- Filters based on the best result's distance
- Uses `DYNAMIC_THRESHOLD_RATIO` (default: 0.7) to calculate threshold
- Formula: `max_allowed_distance = best_distance / ratio`
- Adapts to query quality automatically

### 3. Adaptive Filtering
- Analyzes distance distribution to find quality drops
- Identifies large gaps between consecutive results
- Cuts off results after significant quality drops
- Prevents including poor matches when good ones exist

## Configuration Parameters

### Core Settings

```bash
# Enable/disable distance filtering
ENABLE_DISTANCE_FILTERING=true

# Base distance threshold (0.0 = perfect match, 1.0+ = very different)
BASE_DISTANCE_THRESHOLD=0.8

# Dynamic threshold ratio (lower = more restrictive)
DYNAMIC_THRESHOLD_RATIO=0.7

# Minimum results needed to apply filtering
MIN_RESULTS_FOR_FILTERING=2

# Fallback threshold when filtering fails
FALLBACK_DISTANCE_THRESHOLD=1.0

# Enable detailed debug output
DISTANCE_DEBUG_MODE=false
```

### Parameter Tuning Guide

#### `BASE_DISTANCE_THRESHOLD`
- **0.5-0.6**: Very restrictive, only very similar content
- **0.7-0.8**: Balanced, good for most use cases
- **0.9-1.0**: Permissive, allows more diverse content

#### `DYNAMIC_THRESHOLD_RATIO`
- **0.5-0.6**: Highly selective, prefers very consistent quality
- **0.7-0.8**: Balanced adaptation to query quality
- **0.9-1.0**: More permissive, allows quality variation

#### `MIN_RESULTS_FOR_FILTERING`
- **2**: Apply filtering with minimal results
- **3-5**: Require more results for statistical significance
- **5+**: Only filter when many results available

## Usage Examples

### Basic Usage

The filtering is automatically applied when enabled. No code changes needed:

```python
from rag_processor import RAGProcessor
from chromadb_manager import ChromaDBManager

# Initialize components
chromadb_manager = ChromaDBManager()
chromadb_manager.initialize_client()
rag_processor = RAGProcessor(chromadb_manager)

# Process query with automatic filtering
response = rag_processor.process_query("What is machine learning?")
```

### Direct ChromaDB Query with Filtering

```python
# Query with dynamic filtering
results = chromadb_manager.query_with_dynamic_distance_filter(
    "machine learning concepts", 
    n_results=5
)

# Check filtering information
filtering_info = results.get('filtering_info', {})
print(f"Filtered {filtering_info.get('original_count')} → {filtering_info.get('filtered_count')} results")
```

### Debug Mode

Enable debug mode to see filtering decisions:

```python
from config import config

# Enable debug output
config.DISTANCE_DEBUG_MODE = True

# Process query - will show detailed filtering info
response = rag_processor.process_query("your query here")
```

## Testing and Validation

### Manual Testing

1. **Add diverse content** to your ChromaDB collection
2. **Enable debug mode** (`DISTANCE_DEBUG_MODE=true`)
3. **Test queries** with varying specificity
4. **Observe filtering decisions** in the debug output
5. **Adjust parameters** based on results

### Quality Metrics

Monitor these indicators for optimal performance:

- **Filtering Ratio**: Aim for 30-70% of results being filtered
- **Distance Range**: Best results should be < 0.5 for good matches
- **Response Quality**: Subjectively evaluate answer relevance
- **Coverage**: Ensure important content isn't over-filtered

## Troubleshooting

### Common Issues

#### Over-filtering (Too Few Results)
**Symptoms**: Very short responses, "No relevant information found"
**Solutions**:
- Increase `BASE_DISTANCE_THRESHOLD` (try 0.9)
- Increase `DYNAMIC_THRESHOLD_RATIO` (try 0.8-0.9)
- Decrease `MIN_RESULTS_FOR_FILTERING` (try 1-2)

#### Under-filtering (Poor Quality Results)
**Symptoms**: Responses include irrelevant information
**Solutions**:
- Decrease `BASE_DISTANCE_THRESHOLD` (try 0.6-0.7)
- Decrease `DYNAMIC_THRESHOLD_RATIO` (try 0.5-0.6)
- Increase `MIN_RESULTS_FOR_FILTERING` (try 3-5)

#### Inconsistent Filtering
**Symptoms**: Filtering behavior varies dramatically between queries
**Solutions**:
- Enable `DISTANCE_DEBUG_MODE` to understand decisions
- Check if collection has very diverse content
- Consider using more consistent embedding model
- Adjust `DYNAMIC_THRESHOLD_RATIO` for more stable behavior

### Debug Information

When `DISTANCE_DEBUG_MODE=true`, you'll see output like:

```
--- Distance Filtering Debug Info ---
Query: 'What is machine learning?'
Original results: 8
Filtered results: 3
Distance range: 0.2341 - 0.8765
Base threshold: 0.8
Dynamic ratio: 0.7
Filtered results:
  1. Distance: 0.2341
  2. Distance: 0.3456
  3. Distance: 0.4123
--- End Debug Info ---
```

## Performance Considerations

### Computational Overhead
- Filtering adds minimal processing time
- Most overhead is in the initial ChromaDB query
- Adaptive filtering requires distance analysis but is fast

### Memory Usage
- Queries fetch extra results for filtering (typically 2-3x requested)
- Filtered results are smaller, reducing memory usage downstream
- Overall memory impact is minimal

### Optimization Tips
- Set `MAX_RESULTS` appropriately for your use case
- Use `MIN_RESULTS_FOR_FILTERING` to skip filtering for small result sets
- Enable filtering only when collection has sufficient diversity

## Integration with Enhanced RAG

The distance filtering integrates seamlessly with other MyAI features:

- **Enhanced Formatting**: Filtered results work with all formatting options
- **Interactive Commands**: `/context` and other commands respect filtering settings
- **Multiple Documents**: Filtering works with multi-document retrieval
- **Colorful Output**: Debug information uses the color system

## Best Practices

1. **Start Conservative**: Begin with default settings and adjust based on results
2. **Test Thoroughly**: Use the test script with your actual data
3. **Monitor Quality**: Regularly evaluate response relevance
4. **Document Changes**: Keep track of parameter adjustments and their effects
5. **Use Debug Mode**: Enable debugging when tuning parameters
6. **Consider Content**: Adjust settings based on your document diversity

## Advanced Configuration

### Environment-Specific Settings

Create different configurations for different environments:

```bash
# Development - more permissive for testing
ENABLE_DISTANCE_FILTERING=true
BASE_DISTANCE_THRESHOLD=0.9
DYNAMIC_THRESHOLD_RATIO=0.8
DISTANCE_DEBUG_MODE=true

# Production - more restrictive for quality
ENABLE_DISTANCE_FILTERING=true
BASE_DISTANCE_THRESHOLD=0.7
DYNAMIC_THRESHOLD_RATIO=0.6
DISTANCE_DEBUG_MODE=false
```

### Content-Specific Tuning

Adjust parameters based on your content type:

- **Technical Documentation**: Lower thresholds (0.6-0.7) for precision
- **General Knowledge**: Higher thresholds (0.8-0.9) for coverage
- **Mixed Content**: Balanced settings (0.7-0.8) with adaptive filtering

## Future Enhancements

Planned improvements to the distance filtering system:

- **Machine Learning-based Thresholds**: Automatically learn optimal thresholds
- **Query-specific Filtering**: Adjust filtering based on query characteristics
- **Semantic Clustering**: Group similar results before filtering
- **Performance Metrics**: Built-in quality measurement and reporting
