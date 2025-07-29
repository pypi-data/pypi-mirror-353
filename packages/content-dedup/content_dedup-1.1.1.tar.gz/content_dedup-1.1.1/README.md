# content-dedup

[![PyPI version](https://badge.fury.io/py/content-dedup.svg)](https://badge.fury.io/py/content-dedup)
[![PyPI Downloads](https://static.pepy.tech/badge/content-dedup)](https://pepy.tech/projects/content-dedup)

**Intelligent content deduplication and clustering toolkit with multilingual support, designed for efficient pipeline integration and production use.**

`py-content-dedup` is a powerful Python library and command-line tool that automatically detects and groups similar content items using advanced text similarity algorithms. It supports multiple languages, handles mixed-language content (like Chinese-English), and provides both programmatic API and CLI interfaces for seamless integration into data processing pipelines.

## ✨ Features

- 🌍 **Multilingual Support**: Auto-detection and processing of Chinese, English, Japanese, and mixed-language content
- 🔗 **Smart Clustering**: Groups similar content using TF-IDF, cosine similarity, and advanced text processing
- 🛠️ **Pipeline Ready**: JSON output format with progress logging to stderr (stdout stays clean)
- ⚡ **High Performance**: Optimized field mapping with minimal, balanced, and full mapping options
- 🎯 **Flexible Output**: Support for both full clusters and representative-only output
- 📊 **Detailed Reports**: Comprehensive statistics and language distribution analysis
- 🔧 **Streamlined API**: Simplified field mapping focused on core deduplication functionality

## 🚀 Quick Start

### Installation

#### Basic Installation
```bash
pip install content-dedup
```

#### Full Installation (Recommended)
For complete multilingual support including Chinese text processing:
```bash
pip install content-dedup[full]
```

#### Development Installation
```bash
git clone https://github.com/changyy/py-content-dedup.git
cd py-content-dedup
pip install -e .[dev,full]
```

### Command Line Usage

```bash
# Basic deduplication with auto language detection
content-dedup input.jsonl --output results.json

# Specify language and similarity threshold
content-dedup input.jsonl --language zh --similarity 0.85 --output clusters.json

# Use predefined field mapping for different data formats
content-dedup news_data.jsonl --field-mapping news --output results.json
content-dedup blog_data.jsonl --field-mapping blog --output results.json
content-dedup social_data.jsonl --field-mapping social --output results.json

# Custom field mapping with optimized fields
content-dedup data.jsonl \
  --title-field headline \
  --content-fields body,summary \
  --id-field permalink \
  --category-field tags \
  --output results.json

# Multiple content fields with custom separator
content-dedup data.jsonl \
  --content-fields description,content,text \
  --content-separator ' | ' \
  --output results.json

# Minimal mapping for high performance
content-dedup data.jsonl \
  --title-field headline \
  --content-fields body,summary \
  --id-field permalink \
  --minimal \
  --output results.json

# Pipeline usage with representatives only
content-dedup input.jsonl --format representatives --field-mapping news | jq '.[] | .title'

# Handle missing fields gracefully
content-dedup incomplete_data.jsonl --ignore-missing --title-field title,name --output results.json

# Save both clusters and representatives
content-dedup input.jsonl --output clusters.json --representatives reps.jsonl

# Verbose mode with progress logging
content-dedup input.jsonl --output results.json --verbose --log-file progress.log
```

### Python API Usage

```python
from content_dedup import ContentDeduplicator

# Initialize deduplicator
deduplicator = ContentDeduplicator(
    language='auto',           # Auto-detect language
    similarity_threshold=0.8,  # Similarity threshold for clustering
    mixed_language_threshold=0.3,  # Mixed language detection threshold
    field_mapping='news'       # Use predefined field mapping
)

# Load and process data
deduplicator.load_jsonl('input.jsonl')
clusters = deduplicator.cluster_and_deduplicate()

# Get representatives only
representatives = deduplicator.get_representatives()

# Generate detailed report
report = deduplicator.generate_report()
print(f"Processed {report['basic_statistics']['original_content_count']} items into {len(clusters)} clusters")
```

## 🗂️ Flexible Field Mapping

`py-content-dedup` supports flexible field mapping to handle various JSONL formats without requiring data transformation. We provide **three mapping types** to balance functionality and simplicity:

### 🎯 Field Mapping Options

The library offers optimized field mapping focused on core deduplication functionality:

- **Standard Mapping** (5 fields): Balanced performance and quality - includes title, content, ID, category, and publish time
- **Minimal Mapping** (3 fields): Maximum performance - only title, content, and ID for high-speed processing

### Using Predefined Mappings

```python
from content_dedup import ContentDeduplicator

# Standard mappings (5 fields)
deduplicator = ContentDeduplicator(field_mapping='news')
deduplicator = ContentDeduplicator(field_mapping='blog')

# Balanced mappings (5 essential fields) - RECOMMENDED
deduplicator = ContentDeduplicator(field_mapping='balanced-news')
deduplicator = ContentDeduplicator(field_mapping='balanced-blog')

# Minimal mappings (3 core fields) - HIGH PERFORMANCE
deduplicator = ContentDeduplicator(field_mapping='minimal-news')
deduplicator = ContentDeduplicator(field_mapping='minimal-blog')

# Available presets: 'news', 'blog', 'social', 'academic', 'ecommerce'
# Each with 'balanced-' and 'minimal-' variants
```

### Custom Field Mapping

```python
# Full mapping (all features)
from content_dedup.config.field_mapping import create_custom_mapping
full_mapping = create_custom_mapping(
    title_field='headline',
    content_fields=['body', 'summary'],
    id_field='permalink',
    category_field='tags',
    publish_time_field='published_at',
    content_separator=' | '
)

# Balanced mapping (recommended) - core + important fields
from content_dedup.config.field_mapping_balanced import create_balanced_custom_mapping
balanced_mapping = create_balanced_custom_mapping(
    title_field='headline',
    content_fields=['body', 'summary'],
    id_field='permalink',
    category_field='tags',
    publish_time_field='published_at'
)

# Minimal mapping (performance) - core fields only
from content_dedup.config.field_mapping_minimal import create_minimal_custom_mapping
minimal_mapping = create_minimal_custom_mapping(
    title_field='headline',
    content_fields=['body', 'summary'],
    id_field='permalink'
)

# Use with ContentDeduplicator
deduplicator = ContentDeduplicator(field_mapping=balanced_mapping)  # Recommended
```

### CLI Field Mapping

```bash
# Use predefined mappings
content-dedup data.jsonl --field-mapping news --output results.json
content-dedup data.jsonl --field-mapping balanced-news --output results.json  # Recommended
content-dedup data.jsonl --field-mapping minimal-news --output results.json   # High performance

# Custom field specification (creates balanced mapping)
content-dedup data.jsonl \
  --title-field headline \
  --content-fields body,summary \
  --id-field permalink \
  --category-field tags \
  --output results.json

# Minimal specification for performance
content-dedup data.jsonl \
  --title-field headline \
  --content-fields body,summary \
  --id-field permalink \
  --minimal \
  --output results.json
```

## 📊 Input Format

### Standard Format
Input should be in JSONL format with the following structure:

```json
{
  "title": "Article title",
  "content_text": "Full article content...",
  "url": "https://example.com/article",
  "category": ["news", "technology"],
  "publish_time": "2025/01/15 10:30:00"
}
```

### Custom Formats
With field mapping, you can use any JSONL structure:

```json
// News format
{
  "headline": "Breaking News Title",
  "body": "News content...",
  "summary": "Brief summary...",
  "permalink": "https://news.site/article",
  "tags": ["breaking", "politics"]
}

// Blog format  
{
  "post_title": "Blog Post Title",
  "content": "Blog content...",
  "description": "Post description...",
  "blog_url": "https://blog.site/post",
  "categories": ["tech", "tutorial"]
}

// Social format
{
  "username": "social_user",
  "message": "Social media post content...",
  "post_url": "https://social.site/post/123",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## 📋 Output Formats

### Clusters Format (Default)
```json
{
  "metadata": {
    "total_clusters": 150,
    "original_count": 1000,
    "language_settings": "auto",
    "similarity_threshold": 0.8,
    "compression_ratio": 0.15
  },
  "clusters": [
    {
      "cluster_id": "cluster_0001",
      "representative": { /* ContentItem */ },
      "members": [ /* Array of ContentItems */ ],
      "member_count": 5,
      "dominant_language": "zh",
      "language_distribution": {"zh": 0.8, "en": 0.2}
    }
  ]
}
```

### Representatives Format
```json
[
  { /* Representative ContentItem 1 */ },
  { /* Representative ContentItem 2 */ },
  { /* Representative ContentItem 3 */ }
]
```

### Report Format
```json
{
  "processing_settings": {
    "language_mode": "auto",
    "similarity_threshold": 0.8
  },
  "basic_statistics": {
    "original_content_count": 1000,
    "cluster_count": 150,
    "compression_ratio": "85.00%"
  },
  "language_distribution": {
    "original_language_stats": {"zh": 800, "en": 150, "mixed": 50},
    "mixed_language_cluster_count": 12
  }
}
```

## ⚙️ Configuration Options

### CLI Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--language` | str | `auto` | Language mode: `auto`, `zh`, `en`, `mixed` |
| `--similarity` | float | `0.8` | Similarity threshold for clustering |
| `--mixed-threshold` | float | `0.3` | Mixed language detection threshold |
| `--format` | str | `clusters` | Output format: `clusters`, `representatives`, `report` |
| `--output` | str | - | Output file (JSON). If not specified, outputs to stdout |
| `--representatives` | str | - | Separate file for representatives (JSONL) |
| `--pretty` | bool | `False` | Pretty print JSON output |
| `--verbose` | bool | `False` | Enable verbose logging |
| `--log-file` | str | - | Log file path (default: stderr) |
| `--no-progress` | bool | `False` | Disable progress reporting |

### Language Processing

The tool automatically detects and handles:

- **Chinese (zh)**: Uses jieba for word segmentation (requires `[chinese]` or `[full]` installation)
- **English (en)**: Uses whitespace and punctuation-based tokenization  
- **Mixed Language**: Intelligently separates and processes Chinese-English mixed content
- **Auto Detection**: Analyzes character distribution and content patterns
- **Enhanced Detection**: Uses langdetect library for improved accuracy (requires `[langdetect]` or `[full]` installation)

> **Note**: For optimal Chinese text processing, install with `pip install content-dedup[chinese]` or `pip install content-dedup[full]`. The basic installation provides fallback processing for Chinese text but may have reduced accuracy.

## 🔧 Algorithm Details

### Similarity Calculation

The tool uses a multi-dimensional similarity approach:

1. **Title Similarity** (40%): Sequence-based comparison of titles
2. **Content Similarity** (50%): TF-IDF cosine similarity of processed content
3. **Length Similarity** (10%): Relative length comparison

### Clustering Process

1. **Exact Duplicate Removal**: URL and title hash-based deduplication
2. **Language Detection**: Character-based and statistical language identification
3. **Text Processing**: Language-specific tokenization and stop word removal
4. **Similarity Matrix**: Efficient batch computation of pairwise similarities
5. **Clustering**: Connected components algorithm for grouping similar items
6. **Representative Selection**: Multi-factor scoring for optimal representative selection

### Representative Selection Criteria

Representatives are selected based on:

- **Content Quality** (30%): Length and completeness
- **Title Quality** (20%): Optimal title length and clarity
- **Source Reliability** (20%): Domain-based credibility scoring
- **Timeliness** (20%): Publication time freshness
- **Language Consistency** (10%): Alignment with cluster's dominant language

## 🧪 Examples

### Processing News Articles

```bash
# Process Chinese news with high precision
content-dedup chinese_news.jsonl \
  --language zh \
  --similarity 0.9 \
  --output clusters.json \
  --representatives news_reps.jsonl \
  --verbose

# Pipeline integration for positive news filtering
content-dedup all_news.jsonl --format representatives | \
  python filter_positive_news.py | \
  python generate_summary.py > final_output.json
```

### Mixed Language Content

```bash
# Handle Chinese-English mixed content
content-dedup mixed_content.jsonl \
  --language auto \
  --mixed-threshold 0.2 \
  --similarity 0.85 \
  --format clusters \
  --pretty
```

### Batch Processing

```bash
# Process multiple files
for file in data/*.jsonl; do
  echo "Processing $file..."
  content-dedup "$file" \
    --output "results/$(basename "$file" .jsonl)_clusters.json" \
    --log-file "logs/$(basename "$file" .jsonl).log"
done
```

### Language-Specific Processing

```bash
# For Chinese content (requires chinese installation)
content-dedup chinese_articles.jsonl --language zh --output chinese_clusters.json

# For English content
content-dedup english_articles.jsonl --language en --output english_clusters.json

# For mixed language content (auto-detect)
content-dedup mixed_articles.jsonl --language auto --output mixed_clusters.json
```

## 📚 API Reference

### ContentDeduplicator Class

```python
class ContentDeduplicator:
    def __init__(self, 
                 language: str = 'auto',
                 similarity_threshold: float = 0.8,
                 mixed_language_threshold: float = 0.3,
                 field_mapping: Union[str, Any, None] = None)
    
    def load_jsonl(self, file_path: str) -> None
    def cluster_and_deduplicate(self) -> List[FlexibleContentCluster]
    def generate_report(self) -> Dict[str, Any]
    def save_results(self, output_path: str, format: str = 'clusters') -> None
    def get_representatives(self) -> List[FlexibleContentItem]
    def get_all_clusters(self) -> List[FlexibleContentCluster]
```

### FlexibleContentCluster Class

```python
@dataclass
class FlexibleContentCluster:
    representative: FlexibleContentItem
    members: List[FlexibleContentItem]
    cluster_id: str
    dominant_language: str
    language_distribution: Dict[str, float]
    similarity_scores: Dict[str, float]
```

### FlexibleContentItem Class

```python
@dataclass
class FlexibleContentItem:
    original_data: Dict[str, Any]
    working_fields: Dict[str, Any]
    language: Optional[str] = None
    field_mapping_info: Dict[str, str] = field(default_factory=dict)
    
    @property
    def title(self) -> str
    @property
    def content_text(self) -> str
    @property
    def url(self) -> str
    
    def get_working_field(self, field_name: str, default=None)
    def to_dict(self, mode: str = "working", include_metadata: bool = False) -> Dict[str, Any]
```

## 🛠️ Development

### Setup Development Environment

```bash
git clone https://github.com/changyy/py-content-dedup.git
cd py-content-dedup

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies with full features
pip install -e .[dev,full]

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=content_dedup

# Run specific test file
pytest tests/test_deduplicator.py -v

# Run only fast tests (exclude slow integration tests)
pytest -m "not slow"
```

### Code Quality

```bash
# Format code
black content_dedup/

# Lint code
flake8 content_dedup/

# Type checking
mypy content_dedup/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Install development dependencies: `pip install -e .[dev,full]`
- Run tests before submitting: `pytest`
- Follow code formatting: `black content_dedup/`
- Add tests for new features
- Update documentation as needed

## 💡 Troubleshooting

### Common Issues

**Issue**: ImportError for jieba when processing Chinese text
```bash
# Solution: Install Chinese language support
pip install content-dedup[chinese]
```

**Issue**: Poor language detection accuracy
```bash
# Solution: Install enhanced language detection
pip install content-dedup[langdetect]
```

**Issue**: Reduced performance with English text
```bash
# Solution: Install advanced English processing
pip install content-dedup[english]
```

**Issue**: Missing features or dependencies
```bash
# Solution: Install all features
pip install content-dedup[all]
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [scikit-learn](https://scikit-learn.org/) for machine learning algorithms
- [jieba](https://github.com/fxsjy/jieba) for Chinese word segmentation
- [langdetect](https://github.com/Mimino666/langdetect) for language detection
- [NLTK](https://www.nltk.org/) for natural language processing

## 📞 Support

- 📖 [Documentation](https://github.com/changyy/py-content-dedup/docs)
- 🐛 [Issue Tracker](https://github.com/changyy/py-content-dedup/issues)
- 💬 [Discussions](https://github.com/changyy/py-content-dedup/discussions)

---

**Made with ❤️ for efficient content processing**
