# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'StoreRange'
        db.create_table(u'stock_ranges_storerange', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('store', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Store'])),
            ('rangeType', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('month', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'stock_ranges', ['StoreRange'])

        # Adding model 'ProductRange'
        db.create_table(u'stock_ranges_productrange', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Product'])),
            ('productRange', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('bonus', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('guaranteed', self.gf('django.db.models.fields.CharField')(max_length=4)),
        ))
        db.send_create_signal(u'stock_ranges', ['ProductRange'])

        # Adding model 'StoreDetail'
        db.create_table(u'stock_ranges_storedetail', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stock_ranges.ProductRange'])),
            ('guaranteed', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('passed', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('month', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'stock_ranges', ['StoreDetail'])


    def backwards(self, orm):
        # Deleting model 'StoreRange'
        db.delete_table(u'stock_ranges_storerange')

        # Deleting model 'ProductRange'
        db.delete_table(u'stock_ranges_productrange')

        # Deleting model 'StoreDetail'
        db.delete_table(u'stock_ranges_storedetail')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.brand': {
            'ABN': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'GLN': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'blank': 'True'}),
            'Meta': {'object_name': 'Brand'},
            'actualRebate': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'brand': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'cityState': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'distributor': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.StoreGroup']"}),
            'hasElectronicTrading': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isHOPreferred': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'isInGFK': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'isShared': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'paddress': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pcityState': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'ppostcode': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'purchaser': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'rebate': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'repName': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'repPhone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Store']"}),
            'suburb': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'core.product': {
            'EAN': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'Meta': {'object_name': 'Product'},
            'brand': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Brand']"}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.ProductCategory']"}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'costPrice': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'goPrice': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.StoreGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isCore': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'isGSTExempt': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'isShared': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manWarranty': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'packSize': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'spanNet': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'current'", 'max_length': '20'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Store']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['core.ProductTag']", 'symmetrical': 'False', 'blank': 'True'}),
            'tradePrice': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'})
        },
        u'core.productcategory': {
            'Meta': {'object_name': 'ProductCategory'},
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'extWarrantyTypes': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'extWarrantyTypes_rel_+'", 'null': 'True', 'to': u"orm['core.ProductCategory']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.StoreGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isShared': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'parentCategory': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.ProductCategory']", 'null': 'True', 'blank': 'True'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Store']"})
        },
        u'core.producttag': {
            'Meta': {'object_name': 'ProductTag'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.StoreGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isShared': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Store']"}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'Other'", 'max_length': '10'})
        },
        u'stock_ranges.productrange': {
            'Meta': {'object_name': 'ProductRange'},
            'bonus': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'guaranteed': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Product']"}),
            'productRange': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        },
        u'stock_ranges.storedetail': {
            'Meta': {'object_name': 'StoreDetail'},
            'guaranteed': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month': ('django.db.models.fields.DateTimeField', [], {}),
            'passed': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stock_ranges.ProductRange']"})
        },
        u'stock_ranges.storerange': {
            'Meta': {'object_name': 'StoreRange'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month': ('django.db.models.fields.DateField', [], {}),
            'rangeType': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Store']"})
        },
        u'users.store': {
            'ABN': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'ACN': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'GLN': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'blank': 'True'}),
            'Meta': {'object_name': 'Store'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'companyName': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.StoreGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isHead': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'spanStoreID': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'suburb': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'unique': 'True', 'null': 'True'})
        },
        u'users.storegroup': {
            'Meta': {'object_name': 'StoreGroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.StoreGroup']", 'null': 'True'})
        }
    }

    complete_apps = ['stock_ranges']