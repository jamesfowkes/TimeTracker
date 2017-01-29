from sqlalchemy.sql.expression import func

from TimeTracker.db import db

import logging

def get_module_logger():
    return logging.getLogger(__name__)

def format_address_for_display(address):
    """ Replaces line breaks in client address with HTML breaks """
    return address.replace("\r\n", "<br>")

class Address(db.Model):

    __tablename__ = "Addresses"

    ClientID = db.Column(db.String, db.ForeignKey("Clients.ClientID"), primary_key=True)
    AddressNumber = db.Column(db.Integer, primary_key=True)
    Address = db.Column(db.String)

    def insert(self):
        self.Address = format_address_for_display(self.Address)

        db.session().add(self)
        db.session().commit()

    @staticmethod
    def add_for_client(ClientID, address):
        last = Address.get_for_client(ClientID)
        if len(last) > 0:
            new_address = Address(ClientID=ClientID, AddressNumber=last.AddressNumber+1, Address=address)
        else:
            new_address = Address(ClientID=ClientID, AddressNumber=0, Address=address)
    
        return new_address

    @staticmethod
    def get_for_client(ClientID):
        get_module_logger().info("Getting addresses for ClientID %s", ClientID)

        query = Address.query
        query = query.filter(Address.ClientID==ClientID)
        
        return query.all()
