#!/usr/bin/env python
# -*- coding: utf-8 -*-


from google.appengine.ext import ndb


class Order(ndb.Model):
    order_link = ndb.StringProperty(required=True)
    order_number = ndb.IntegerProperty(required=True)
    order_status = ndb.StringProperty()
    order_delivery_date = ndb.DateProperty()

    job_number = ndb.IntegerProperty()
    records_link = ndb.StringProperty()

    @classmethod
    def get_all(cls):
        return cls.query()

    @classmethod
    def get_or_create(cls):
        pass


class Elite(Order):
    color = ndb.StringProperty(required=True)
    streamer = ndb.StringProperty()
    accessories = ndb.JsonProperty()
