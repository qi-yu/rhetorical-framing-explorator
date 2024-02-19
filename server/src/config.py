class Config:
    RAW_FILE_PATH = "./upload"
    TEMP_FILE_PATH = "./temp"
    PREPROCESSED_FILE_PATH = "./output"
    PROGRESS_PATH = "./progress"
    STATISTICS_DOCUMENT_LEVEL_PATH = "./statistics/document_level_statistics.tsv"
    STATISTICS_SENTENCE_LEVEL_PATH = "./statistics/sentence_level_statistics.tsv"
    STATISTICS_BY_LABEL_PATH = "./statistics/feature_statistics_by_label.tsv"
    FEATURE_CONFIG_PATH = "./src/features.json"
    PREPROCESSING_SCRIPT_PATH = './src/app/preprocessing.py'
    ANNOTATION_SCRIPT_PATH = './src/app/annotating.py'
    WORD_LIST_BASE_PATH = "./src/app/wordlists"