# RelationExtraction

Some utility scripts for the relation extraction task.

## semeval2018format

Allow to transform the semEval2018 task 7 data to the semEval2010 task 8 format.

### Command line interface usage

To prompt the help menu :
```python3 semeval2018to2010format.py -h```

Example commands for Training file and test file creation :
```python3 semeval2018to2010format.py -xml 1.1.text.xml -rel 1.1.relations.txt -out TRAIN.TXT```

```python3 semeval2018to2010format.py -xml 2.test.text.xml -rel keys.test.2.txt -out TEST.TXT ```

#### Options

Remove the comment line with the nc flag :
```python3 semeval2018to2010format.py -xml 2.test.text.xml -rel keys.test.2.txt -out TEST_nocomment_noindex.TXT -nc```

Remove the index information with the ni flag :
```python3 semeval2018to2010format.py -xml 2.test.text.xml -rel keys.test.2.txt -out TEST_noindex.TXT -ni```

Surround text field with double quote using the dq flag :
```python3 semeval2018to2010format.py -xml 2.test.text.xml -rel keys.test.2.txt -out TEST_quote.TXT -dq```

All flags can be used together.

### Result

Result files are already there under the names : TRAIN.TXT and TEST.TXT and other variants

# Contacts

gael dot guibon at gmail.com
gael dot guibon at lis-lab.fr

@2018 LIS-CNRS
