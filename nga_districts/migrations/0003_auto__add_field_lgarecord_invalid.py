# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'LGARecord.invalid'
        db.add_column('nga_districts_lgarecord', 'invalid', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'LGARecord.invalid'
        db.delete_column('nga_districts_lgarecord', 'invalid')


    models = {
        'facilities.variable': {
            'Meta': {'object_name': 'Variable'},
            'data_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'load_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '128', 'primary_key': 'True'})
        },
        'nga_districts.lga': {
            'Meta': {'object_name': 'LGA'},
            'afr_id': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'data_available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'data_load_in_progress': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'data_loaded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'geoid': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'included_in_malaria_survey': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'kml_id': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'latlng_str': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'scale_up': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'lgas'", 'to': "orm['nga_districts.State']"}),
            'survey_round': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'unique_slug': ('django.db.models.fields.TextField', [], {'null': 'True'})
        },
        'nga_districts.lgarecord': {
            'Meta': {'object_name': 'LGARecord'},
            'boolean_value': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'float_value': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lga': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'data_records'", 'to': "orm['nga_districts.LGA']"}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'string_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'variable': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['facilities.Variable']"})
        },
        'nga_districts.state': {
            'Meta': {'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'states'", 'to': "orm['nga_districts.Zone']"})
        },
        'nga_districts.zone': {
            'Meta': {'object_name': 'Zone'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        }
    }

    complete_apps = ['nga_districts']
