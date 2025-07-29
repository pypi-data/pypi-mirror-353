# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


from typing import Annotated, Union

from pydantic import Field

from ibm_watsonx_gov.entities.metric import GenAIMetric

from .answer_relevance.answer_relevance_metric import AnswerRelevanceMetric
from .answer_similarity.answer_similarity_metric import AnswerSimilarityMetric
from .average_precision.average_precision_metric import AveragePrecisionMetric
from .faithfulness.faithfulness_metric import FaithfulnessMetric
from .hit_rate.hit_rate_metric import HitRateMetric
from .llm_validation.llm_validation_metric import LLMValidationMetric
from .ndcg.ndcg_metric import NDCGMetric
from .prompt_safety_risk.prompt_safety_risk_metric import \
    PromptSafetyRiskMetric
from .reciprocal_rank.reciprocal_rank_metric import ReciprocalRankMetric
from .retrieval_precision.retrieval_precision_metric import \
    RetrievalPrecisionMetric
from .tool_calling_hallucination.tool_calling_hallucination_metric import \
    ToolCallingHallucinationMetric
from .unsuccessful_requests.unsuccessful_requests_metric import \
    UnsuccessfulRequestsMetric
from .prompt_safety_risk.prompt_safety_risk_metric import PromptSafetyRiskMetric
from .llm_validation.llm_validation_metric import LLMValidationMetric
from .hap.hap_metric import HAPMetric
from .pii.pii_metric import PIIMetric
from .context_relevance.context_relevance_metric import ContextRelevanceMetric  # isort:skip
from .harm.harm_metric import HarmMetric
from .social_bias.social_bias_metric import SocialBiasMetric
from .profanity.profanity_metric import ProfanityMetric
from .sexual_content.sexual_content_metric import SexualContentMetric
from .unethnical_behavior.unethnical_behavior_metric import UnethnicalBehaviorMetric
from .violence.violence_metric import ViolenceMetric
from .harm_engagement.harm_engagement_metric import HarmEngagementMetric
from .evasiveness.evasiveness_metric import EvasivenessMetric
from .jailbreak.jailbreak_metric import JailbreakMetric

METRICS_UNION = Annotated[Union[tuple(GenAIMetric.__subclasses__())], Field(
    discriminator="name")]
