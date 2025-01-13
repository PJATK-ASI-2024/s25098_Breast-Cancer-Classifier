import pandas as pd
from tpot import TPOTClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, mean_absolute_error
from sklearn.metrics import accuracy_score, mean_absolute_error, precision_score, recall_score, f1_score

data = pd.read_csv('../data/cleaned_data.csv')

X = data.drop(columns=['Status'])
y = data['Status']

y_encoder = LabelEncoder()
y = y_encoder.fit_transform(y)

for col in X.select_dtypes(include=[object]).columns:
    x_encoder = LabelEncoder()
    X[col] = x_encoder.fit_transform(X[col])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

tpot = TPOTClassifier(generations=5, population_size=50, random_state=42, verbosity=2)
tpot.fit(X_train, y_train)

evaluated_pipelines = sorted(
    tpot.evaluated_individuals_.items(),
    key=lambda x: x[1]['internal_cv_score'],
    reverse=True
)

unique_classifiers = set()

print("\nTop 3 best pipelines:")
for i, (pipeline_name, pipeline_info) in enumerate(evaluated_pipelines[:5], start=1):
    classifier_name = pipeline_name.split('(')[0]
    if classifier_name not in unique_classifiers:
        unique_classifiers.add(classifier_name)
        print(f"\nPipeline {i}:")
        print(f"Name: {pipeline_name}")
        print(f"Internal CV Score: {pipeline_info['internal_cv_score']}")

tpot.export('best_model.py')
