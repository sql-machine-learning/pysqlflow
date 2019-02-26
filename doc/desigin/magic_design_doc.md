# Magic Command Design Doc

## Overview

Magic command wraps a pysqlflow client. It pretty prints the logs and tables.

## Example

Magic command can be invoked through `%%sqlflow`.

```
In [1]: %load_ext sqlflow

In [2]: %%sqlflow select * from iris.iris limit 1;
Out[2]: executing query 100% [========================================]
+--------------+-------------+--------------+-------------+-------+
| sepal_length | sepal_width | petal_length | petal_width | class |
+--------------+-------------+--------------+-------------+-------+
|          6.4 |         2.8 |          5.6 |         2.2 |     2 |
+--------------+-------------+--------------+-------------+-------+

In [3]: %%sqlflow select *
   ...: from iris.iris limit 1;
   ...:
Out[3]: executing query 100% [========================================]
+--------------+-------------+--------------+-------------+-------+
| sepal_length | sepal_width | petal_length | petal_width | class |
+--------------+-------------+--------------+-------------+-------+
|          6.4 |         2.8 |          5.6 |         2.2 |     2 |
+--------------+-------------+--------------+-------------+-------+

In [4]: %%sqlflow SELECT *
   ...: FROM iris.iris limit 1
   ...: TRAIN DNNClassifier
   ...: WITH
   ...:   n_classes = 3,
   ...:   hidden_units = [10, 20]
   ...: COLUMN sepal_length, sepal_width, petal_length, petal_width
   ...: LABEL class
   ...: INTO my_dnn_model;
Out[4]:
Epoch 0: Training Accuracy ... Validation Accuracy ...
Epoch 1: Training Accuracy ... Validation Accuracy ...
Epoch 2: Training Accuracy ... Validation Accuracy ...
...
Train Finished. Model saved at my_dnn_model
```

## Implementation

### Pretty print

#### Table

Some off-the-shelf library: https://stackoverflow.com/a/26937531/6794675

```
>>> from prettytable import PrettyTable
>>> t = PrettyTable(['Name', 'Age'])
>>> t.add_row(['Alice', 24])
>>> t.add_row(['Bob', 19])
>>> print t
+-------+-----+
|  Name | Age |
+-------+-----+
| Alice |  24 |
|  Bob  |  19 |
+-------+-----+
```

#### Log

Progress bar: https://stackoverflow.com/questions/3002085/python-to-print-out-status-bar-and-percentage

```text
[================          ]  60%
```
