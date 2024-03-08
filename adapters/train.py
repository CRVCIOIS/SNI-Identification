"""
Provides an adapter for training-related information in MongoDB.
"""

from classes.mongo import DBInterface, Schema

class TrainAdapter(DBInterface):
    """
    Performs operations on training data and the related mongo collections.

    Example usage:
            ```
            train_adapter = TrainAdapter()
            train_adapter.insert_to_train_set(data)
            ```
    """

    def insert_to_train_set(self, data):
        """
        Inserts the given data into the train set collection in the MongoDB database.

        Parameters:
            data (dict): The data to be inserted into the train set collection.

        Returns:
            None
        """
        self.mongo_client[Schema.DB][Schema.TRAIN_SET].insert_one(data)
        
    def insert_to_dev_set(self, data):
        """
        Inserts the given data into the development set collection in the MongoDB database.

        Parameters:
            data (dict): The data to be inserted into the development set.

        Returns:
            None
        """
        self.mongo_client[Schema.DB][Schema.DEV_SET].insert_one(data)
    
    def insert_to_test_set(self, data):
        """
        Inserts the given data into the test set collection in the MongoDB database.

        Parameters:
            data (dict): The data to be inserted into the test set.

        Returns:
            None
        """
        self.mongo_client[Schema.DB][Schema.TEST_SET].insert_one(data)
    
    def fetch_train_set(self):
        """
        Fetch the training set from the database.

        returns:
            the training set
        """
        return self.mongo_client[Schema.DB][Schema.TRAIN_SET].find()
    
    def fetch_dev_set(self):
        """
        Fetch the dev set from the database.

        returns:
            the development set
        """
        return self.mongo_client[Schema.DB][Schema.DEV_SET].find()
    
    def fetch_test_set(self):
        """
        Fetch the test set from the database.

        returns:
            the test set
        """
        return self.mongo_client[Schema.DB][Schema.TEST_SET].find()

    def delete_train_set(self):
        """
        Deletes the training set from the database.
        """
        self.mongo_client[Schema.DB][Schema.TRAIN_SET].delete_many({})
        
    def delete_dev_set(self):
        """
        Deletes the development set from the database.
        """
        self.mongo_client[Schema.DB][Schema.DEV_SET].delete_many({})
        
    def delete_test_set(self):
        """
        Deletes the test set from the database.
        """
        self.mongo_client[Schema.DB][Schema.TEST_SET].delete_many({})

    def delete_all_data_sets(self):
        """
        Deletes all data sets from the database.
        """
        self.delete_train_set()
        self.delete_dev_set()
        self.delete_test_set()