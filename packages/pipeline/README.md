# grounding-pipeline

Claim-level grounding guard의 **핵심 로직** 패키지.

나중에 여기 들어올 것:

1. retrieve
2. cite-forced generate
3. claim split
4. verify (`supported | partial | unsupported | uncited`)
5. filter / refuse
6. evidence report

지금은 스캐폴드만 있음. API(`services/api`)가 이 패키지를 import해서 쓴다.
