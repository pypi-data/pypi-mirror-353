import numpy as np
from hmmlearn import hmm
from sklearn_crfsuite import CRF
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Toy dataset for sequence tagging
X = [['walk', 'in', 'the', 'park'],
     ['eat', 'apple'],
     ['eat', 'apple', 'in', 'the', 'morning']]

y = [['V', 'P', 'D', 'N'],
     ['V', 'N'],
     ['V', 'N', 'P', 'D', 'N']]

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Hidden Markov Model (HMM)
hmm_model = hmm.MultinomialHMM(n_components=3)  # Number of states
hmm_model.fit(np.concatenate(X_train),
             [len(seq) for seq in X_train],
             [item for sublist in y_train for item in sublist])

# Conditional Random Fields (CRF)
crf_model = CRF()
crf_model.fit(X_train, y_train)

# Evaluation
print("HMM Results:")
hmm_pred = hmm_model.predict(np.concatenate(X_test),
                           [len(seq) for seq in X_test])
print(classification_report([item for sublist in y_test for item in sublist],
                          [item for sublist in hmm_pred for item in sublist]))

print("\nCRF Results:")
crf_pred = crf_model.predict(X_test)
print(classification_report([item for sublist in y_test for item in sublist],
                          [item for sublist in crf_pred for item in sublist]))