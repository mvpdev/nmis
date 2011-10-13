# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Variable.load_order'
        db.add_column('facilities_variable', 'load_order', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Variable.load_order'
        db.delete_column('facilities_variable', 'load_order')


    models = {
        'facilities.calculatedvariable': {
            'Meta': {'object_name': 'CalculatedVariable', '_ormbases': ['facilities.Variable']},
            'formula': ('django.db.models.fields.TextField', [], {}),
            'variable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['facilities.Variable']", 'unique': 'True', 'primary_key': 'True'})
        },
        'facilities.facility': {
            'Meta': {'object_name': 'Facility'},
            'facility_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'facility_type': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['facilities.FacilityType']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lga': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'facilities'", 'null': 'True', 'to': "orm['nga_districts.LGA']"}),
            'sector': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['facilities.Sector']", 'null': 'True'})
        },
        'facilities.facilityrecord': {
            'Meta': {'object_name': 'FacilityRecord'},
            'boolean_value': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'facility': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'data_records'", 'to': "orm['facilities.Facility']"}),
            'float_value': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'string_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'variable': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['facilities.Variable']"})
        },
        'facilities.facilitytype': {
            'Meta': {'object_name': 'FacilityType'},
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'facilities.gapvariable': {
            'Meta': {'object_name': 'GapVariable', '_ormbases': ['facilities.Variable']},
            'target': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'gaps_using_targets'", 'to': "orm['facilities.Variable']"}),
            'variable': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'gaps_using_actuals'", 'to': "orm['facilities.Variable']"}),
            'variable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['facilities.Variable']", 'unique': 'True', 'primary_key': 'True'})
        },
        'facilities.keyrename': {
            'Meta': {'unique_together': "(('data_source', 'old_key'),)", 'object_name': 'KeyRename'},
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_key': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'old_key': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'facilities.lgaindicator': {
            'Meta': {'object_name': 'LGAIndicator', '_ormbases': ['facilities.Variable']},
            'method': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'lga_indicators'", 'to': "orm['facilities.Variable']"}),
            'sector': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['facilities.Sector']", 'null': 'True'}),
            'variable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['facilities.Variable']", 'unique': 'True', 'primary_key': 'True'})
        },
        'facilities.partitionvariable': {
            'Meta': {'object_name': 'PartitionVariable', '_ormbases': ['facilities.CalculatedVariable']},
            'calculatedvariable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['facilities.CalculatedVariable']", 'unique': 'True', 'primary_key': 'True'}),
            'partition': ('django.db.models.fields.TextField', [], {})
        },
        'facilities.sector': {
            'Meta': {'object_name': 'Sector'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '128', 'primary_key': 'True'})
        },
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

    complete_apps = ['facilities']
