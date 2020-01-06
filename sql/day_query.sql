WITH ALL_CASES AS (
    SELECT P.SOLAR_BILLING_ACCOUNT_NUMBER AS BILLING_ACCOUNT
         , CASE
        -- ADD DEFAULT CASES
               WHEN C.RECORD_TYPE ILIKE '%DEFAULT%'
                   AND C.PRIMARY_REASON ILIKE '%FORE%'
                   AND C.STATUS NOT ILIKE '%CLOSE%'
                   THEN 'FORE'
               WHEN C.RECORD_TYPE ILIKE '%DEFAULT%'
                   AND C.PRIMARY_REASON ILIKE '%DECEASED%'
                   AND C.STATUS NOT ILIKE '%CLOSE%'
                   THEN 'DCNT'
               WHEN C.RECORD_TYPE ILIKE '%DEFAULT%'
                   AND C.STATUS NOT ILIKE '%CLOSE%'
                   THEN 'CORP'
               WHEN C.RECORD_TYPE ILIKE '%ESCAL%'
                   AND C.EXECUTIVE_RESOLUTIONS_ACCEPTED IS NULL
                   AND C.SOLAR_QUEUE ILIKE '%DISPUTE%'
                   AND C.STATUS NOT ILIKE '%CLOSE%'
                   THEN 'CORP'
        -- REMOVE DEFAULT CASES
               WHEN C.RECORD_TYPE ILIKE '%DEFAULT%'
                   AND C.PRIMARY_REASON ILIKE '%FORE%'
                   AND C.STATUS NOT ILIKE '%CLOSE%'
                   THEN 'NONE'
               WHEN C.RECORD_TYPE ILIKE '%DEFAULT%'
                   AND C.PRIMARY_REASON ILIKE '%DECEASED%'
                   AND C.STATUS NOT ILIKE '%CLOSE%'
                   THEN 'NONE'
               WHEN C.RECORD_TYPE ILIKE '%DEFAULT%'
                   AND C.STATUS NOT ILIKE '%CLOSE%'
                   THEN 'NONE'
               WHEN C.RECORD_TYPE ILIKE '%ESCAL%'
                   AND C.EXECUTIVE_RESOLUTIONS_ACCEPTED IS NULL
                   AND C.SOLAR_QUEUE ILIKE '%DISPUTE%'
                   AND C.STATUS NOT ILIKE '%CLOSE%'
                   THEN 'NONE'
        -- ADD ERT CASES
               WHEN C.RECORD_TYPE ILIKE '%ESCALAT%'
                   AND C.EXECUTIVE_RESOLUTIONS_ACCEPTED IS NOT NULL
                   AND C.STATUS ILIKE '%DISPUTE%'
                   THEN 'LWST'
               WHEN C.RECORD_TYPE ILIKE '%ESCALAT%'
                   AND C.EXECUTIVE_RESOLUTIONS_ACCEPTED IS NOT NULL
                   AND C.STATUS NOT ILIKE '%CLOSE%'
                   THEN 'CMLT'
        -- REMOVE ERT CASES
               WHEN C.RECORD_TYPE ILIKE '%ESCALAT%'
                   AND C.EXECUTIVE_RESOLUTIONS_ACCEPTED IS NOT NULL
                   AND C.STATUS ILIKE '%CLOSE%'
                   THEN 'NONE'
        END                               AS NEW_ACCOUNT_CODE
         , CURRENT_DATE                   AS DATE_REQUESTED
    FROM RPT.T_CASE AS C
             LEFT JOIN RPT.T_PROJECT AS P
                       ON P.PROJECT_ID = C.PROJECT_ID
    WHERE (
            (
                        C.RECORD_TYPE IN ('Solar - Customer Default', 'Solar - Customer Escalation')
                    AND C.EXECUTIVE_RESOLUTIONS_ACCEPTED IS NULL
                    AND C.SUBJECT NOT ILIKE '%D3%'
                )
            OR (
                    C.RECORD_TYPE IN ('Solar - Customer Escalation')
                    AND C.EXECUTIVE_RESOLUTIONS_ACCEPTED IS NOT NULL
                )
        )
      AND (
                DATE_TRUNC(dd, C.CREATED_DATE) = DATEADD(dd,
                                                         IFF(DAYNAME(CURRENT_DATE) = 'Mon', -3, -1),
                                                         CURRENT_DATE)
            OR DATE_TRUNC(dd, C.CLOSED_DATE) = DATEADD(dd,
                                                       IFF(DAYNAME(CURRENT_DATE) = 'Mon', -3, -1),
                                                       CURRENT_DATE)
        )
)

SELECT *
FROM ALL_CASES
WHERE NEW_ACCOUNT_CODE IS NOT NULL
ORDER BY NEW_ACCOUNT_CODE