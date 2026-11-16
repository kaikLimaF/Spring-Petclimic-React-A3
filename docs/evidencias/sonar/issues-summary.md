| # | Tipo | Severidade | Regra | Arquivo | Linha | Mensagem |
|---|---|---|---|---|---|---|
| 1 | BUG | CRITICAL | java:S8975 | JpaOwnerRepositoryImpl.java | 79 | Use the return value of "merge()". |
| 2 | BUG | CRITICAL | java:S8975 | JpaPetRepositoryImpl.java | 63 | Use the return value of "merge()". |
| 3 | BUG | CRITICAL | java:S8975 | JpaPetTypeRepositoryImpl.java | 70 | Use the return value of "merge()". |
| 4 | BUG | CRITICAL | java:S8975 | JpaSpecialtyRepositoryImpl.java | 68 | Use the return value of "merge()". |
| 5 | BUG | CRITICAL | java:S8975 | JpaUserRepositoryImpl.java | 24 | Use the return value of "merge()". |
| 6 | BUG | CRITICAL | java:S8975 | JpaVetRepositoryImpl.java | 61 | Use the return value of "merge()". |
| 7 | BUG | CRITICAL | java:S8975 | JpaVisitRepositoryImpl.java | 55 | Use the return value of "merge()". |
| 8 | VULNERABILITY | CRITICAL | java:S4502 | BasicAuthenticationConfig.java | 35 | Make sure disabling Spring Security's CSRF protection is safe here. |
| 9 | VULNERABILITY | CRITICAL | java:S5344 | BasicAuthenticationConfig.java | 43 | Don't use the default "PasswordEncoder" relying on plain-text. |
| 10 | VULNERABILITY | CRITICAL | java:S4502 | DisableSecurityConfig.java | 25 | Make sure disabling Spring Security's CSRF protection is safe here. |
| 11 | VULNERABILITY | CRITICAL | java:S4502 | WebSecurityConfig.java | 24 | Make sure disabling Spring Security's CSRF protection is safe here. |
| 12 | VULNERABILITY | MAJOR | java:S2077 | JpaPetRepositoryImpl.java | 77 | Make sure using a dynamically formatted SQL query is safe here. |
| 13 | VULNERABILITY | MAJOR | java:S2077 | JpaPetRepositoryImpl.java | 78 | Make sure using a dynamically formatted SQL query is safe here. |
| 14 | VULNERABILITY | MAJOR | java:S2077 | SpringDataPetRepositoryImpl.java | 39 | Make sure using a dynamically formatted SQL query is safe here. |
| 15 | VULNERABILITY | MAJOR | java:S2077 | SpringDataPetRepositoryImpl.java | 40 | Make sure using a dynamically formatted SQL query is safe here. |
| 16 | VULNERABILITY | MAJOR | java:S2077 | SpringDataVisitRepositoryImpl.java | 40 | Make sure using a dynamically formatted SQL query is safe here. |
| 17 | VULNERABILITY | MAJOR | java:S5122 | OwnerRestController.java | 48 | Make sure that enabling CORS is safe here. |
| 18 | VULNERABILITY | MAJOR | java:S5122 | PetRestController.java | 39 | Make sure that enabling CORS is safe here. |
| 19 | VULNERABILITY | MAJOR | java:S5122 | PetTypeRestController.java | 38 | Make sure that enabling CORS is safe here. |
| 20 | VULNERABILITY | MAJOR | java:S5122 | RootRestController.java | 34 | Make sure that enabling CORS is safe here. |
| 21 | VULNERABILITY | MAJOR | java:S5122 | SpecialtyRestController.java | 40 | Make sure that enabling CORS is safe here. |
| 22 | VULNERABILITY | MAJOR | java:S5122 | UserRestController.java | 36 | Make sure that enabling CORS is safe here. |
| 23 | VULNERABILITY | MAJOR | java:S5122 | VetRestController.java | 42 | Make sure that enabling CORS is safe here. |
| 24 | VULNERABILITY | MAJOR | java:S5122 | VisitRestController.java | 40 | Make sure that enabling CORS is safe here. |
| 25 | VULNERABILITY | MINOR | java:S4507 | ExceptionControllerAdvice.java | 50 | Make sure this debug feature is deactivated before delivering the code in production. |
| 26 | VULNERABILITY | MINOR | java:S4507 | BindingErrorsResponse.java | 89 | Make sure this debug feature is deactivated before delivering the code in production. |
| 27 | VULNERABILITY | MINOR | java:S3752 | RootRestController.java | 41 | Explicitly specify the HTTP methods this endpoint accepts. |
| 28 | CODE_SMELL | MAJOR | java:S6813 | BasicAuthenticationConfig.java | 22 | Remove this field injection and use constructor injection instead. |
| 29 | CODE_SMELL | MAJOR | java:S6813 | UserServiceImpl.java | 13 | Remove this field injection and use constructor injection instead. |
