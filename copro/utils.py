import logging
import pandas as pd

from enum import Enum


logger = logging.getLogger(__name__)


class CSVCol(Enum):
    """
    Enumeration for CSV columns with their labels, 
    data types, and whether to clear NA values.
    """
    REFERENCE_NUMBER = 'REFERENCE_NUMBER', 'str'
    AD_URLS = 'AD_URLS', 'str'
    DEPT_CODE = 'DEPT_CODE', 'category'
    ZIP_CODE = 'ZIP_CODE', 'category'
    CITY = 'CITY', 'category'
    CONDOMINIUM_EXPENSES = 'CONDOMINIUM_EXPENSES', 'float32'

    @property
    def label(self):
        """Return the label of the column."""
        return self.value[0]

    @property
    def dtype(self):
        """Return the data type of the column."""
        return self.value[1]

    @property
    def clear_na(self):
        """Return whether to clear NA values for the column."""
        return self.value[2]

    @classmethod
    def labels(cls):
        """Return a list of column labels."""
        return [col.label for col in cls]

    @classmethod
    def dtypes(cls):
        """Return a dictionary of column labels and their data types."""
        return {col.label: col.dtype for col in cls}
    

class CSVService:
    """Service to handle CSV file reading and cleaning."""
    _dataframe = None

    def __init__(
        self, 
        csv_path, 
        chunksize=50_000, 
    ):
        self._csv_path = csv_path
        self.chunksize = chunksize

        self._set_reader()

    def _set_reader(self):
        """Set the CSV reader."""
        self._reader = pd.read_csv(
            self._csv_path,
            chunksize=self.chunksize,
            usecols=CSVCol.labels(),
            dtype=CSVCol.dtypes(),
        )

    def _clean_chunk(self, chunk, chunk_id=None):
        """Clean a chunk of the DataFrame by dropping rows with NA values"""
        original_size = len(chunk)
        cleaned_chunk = chunk.dropna()
        cleaned_chunk = cleaned_chunk[cleaned_chunk[CSVCol.CONDOMINIUM_EXPENSES.label] != 0]
        cleaned_size = len(cleaned_chunk)

        logger.info(
            f"[Chunk {chunk_id}] lines before cleaning : {original_size}, after : {cleaned_size} "
            f"({original_size - cleaned_size} deleted lines)" 
        )

        return cleaned_chunk.reset_index(drop=True)

    def get_cleaned_chunks(self):
        """ Generator to yield cleaned chunks of the CSV file."""
        for chunk_id, chunk in enumerate(self._reader):
            cleaned_chunk = self._clean_chunk(chunk, chunk_id)
            if not cleaned_chunk.empty:
                yield cleaned_chunk
                