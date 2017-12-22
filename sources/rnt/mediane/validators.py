from django.core.exceptions import ValidationError

from mediane.process import evaluate_dataset_and_provide_stats


def sound_dataset_validator(value):
    evaluation = evaluate_dataset_and_provide_stats(value.split('\n'))
    if evaluation['invalid']:
        raise ValidationError(
            "content attribute must contains a valid dataset: %s" %
            ', '.join(['line %i: %s' % (k, v) for k, v in evaluation["invalid_rankings_id"].items()]),
        )
    return evaluation
