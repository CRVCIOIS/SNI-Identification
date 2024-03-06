"""
Provides an adapter for training-related information in MongoDB.
"""

from classes.mongo import DBInterface, Schema

class TrainAdapter(DBInterface):
    """
    Class for interfacing with the SCB API and the MongoDB database.

    Example usage:
            ```
            scb = SCBinterface()
            scb.fetch_companies_from_api(
                sni_start="00000",
                sni_stop="02300", 
                fetch_limit=10)
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
    
    def fetch_train_set(self):
        """
        Fetch the training set from the database.

        returns:
            the training set
        """
        return self.mongo_client[Schema.DB][Schema.TRAIN_SET].find()
    
    def fetch_dev_set(self):
        """
        Fetch the training set from the database.

        returns:
            the training set
        """
        return self.mongo_client[Schema.DB][Schema.DEV_SET].find()
