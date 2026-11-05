# Copyright, Attribution and Legal Review of Three Actual Advisor Outputs

**Status:** Three actual advisor outputs have now been reviewed from the saved conversation transcript `Pasted text(8).txt` (captured 4 November 2026). This is an educational risk review, not a legal opinion or proof of copyright clearance.

**Evidence limits:** The saved transcript contains the exact question, answer text and displayed source titles for the three examples below. It does not preserve the original model identifier, timestamp for each response, or canonical source URLs attached to the original citations. Those fields are marked as not captured rather than reconstructed as if they were in the transcript.

## Sample 1 — Undergraduate programme directory

- **Question:** "programmes offered at vu"
- **Generated answer:** A seven-row summary of undergraduate programme families: B.Tech CSE with Data Science/AI & ML specialisations, B.A. Economics, B.A. Psychology, B.Des, B.M.S. Digital Business, integrated B.A. LL.B. and integrated B.M.S. LL.B.

**Saved response extract (transcribed from the actual conversation):**

> Vidyashilp University — Undergraduate Programmes
>
> - Engineering & Technology: B.Tech Computer Science and Engineering (specialisations: Data Science; Artificial Intelligence & Machine Learning)
> - Liberal Arts & Sciences: B.A. Economics; B.A. Psychology
> - Design: B.Des (Design)
> - Management & Business: B.M.S. Digital Business
> - Law (Integrated): Integrated B.A. LL.B.; Integrated B.M.S. LL.B.
>
> Sources: the university homepage and programme directory.

- **Displayed source titles:** "Vidyashilp University — Homepage" and "Undergraduate Programmes and Areas of Study"; the saved transcript also lists "Study at VU / Admissions" and school pages.
- **Canonical source pages for review:** https://vidyashilp.edu.in/ and https://vidyashilp.edu.in/#academics
- **Model/date:** Model identifier not preserved in the saved transcript; transcript capture date 4 November 2026.
- **Accuracy / authority risk:** Medium. It is a concise summary, but programme names, award titles and active status can change. The answer should be read as a summary of the pages fetched, not an admission guarantee or complete programme catalogue.
- **Copyright / attribution risk:** Low to medium. The response is a short factual list in the advisor's own table format, not a reproduction of full webpage text or artwork. The source pages should remain attributed, and VU logos, photographs and full brochure text should not be copied without permission.
- **Recommended practice:** Keep the source links visible, add a retrieval date to saved evidence, and tell students to confirm current admissions and eligibility with VU.

## Sample 2 — Calculus course-code lookup

- **Question:** "course code of calculus"
- **Generated answer:** MATH201, with batch-specific rows for B.Tech batches 2022, 2023 and 2024. The transcript reports semesters 1, 2 and 2 respectively, three credits, and no prerequisite listed. It explicitly says the source does not specify a track for those batches.

**Saved response extract (transcribed from the actual conversation):**

> Calculus — course details
>
> The course code in the available B.Tech semester-spread records is MATH201.
>
> | Admission batch | Course code | Semester | Credits | Prerequisite | Track in source |
> |---|---|---:|---:|---|---|
> | 2022 | MATH201 | 1 | 3 | None listed | Not specified |
> | 2023 | MATH201 | 2 | 3 | None listed | Not specified |
> | 2024 | MATH201 | 2 | 3 | None listed | Not specified |
>
> The source only identifies the 2026 records as Data Science. The 2022–2025 records do not specify a specialisation, so their track should not be inferred.

- **Displayed source title:** `VU_Semester_Data_Split.zip · 01_Semester_Spread_BTech_2022.xlsx`, with source workbook and cell coordinates shown for the 2022 row.
- **Canonical source file:** https://github.com/goury-nandana/vu-academic-advisor-gai-a2/blob/main/VU_Semester_Data_Split.zip
- **Model/date:** Model identifier not preserved in the saved transcript; transcript capture date 4 November 2026.
- **Accuracy / authority risk:** Low to medium. The batch distinctions and "not specified" language are appropriate. The response should still be checked against the correct workbook row for each batch before a student makes a registration decision.
- **Copyright / attribution risk:** Low. Course codes, titles, credit values and semester numbers are factual data. The application presents a compact factual extract and identifies the workbook/source row rather than reproducing the workbook wholesale.
- **Recommended practice:** Preserve batch, semester, source workbook and cell-level provenance. Never infer a specialisation from a batch where the workbook does not identify one.

## Sample 3 — B.Tech minor options for the 2022 batch

- **Question:** "minors offered for btech for teh year 2022"
- **Generated answer:** Design, Psychology, Economics, Finance and Marketing are listed as minor disciplines recorded for the 2022 admission batch. The answer also says that a listed minor is not guaranteed to run and states the Student Handbook's ten-student registration threshold, subject to a Programme Chair exception.

**Saved response extract (transcribed from the actual conversation):**

> B.Tech minor options recorded by admission batch
>
> 2022 batch: Design, Psychology, Economics, Finance, Marketing.
>
> Important: A minor appearing in the workbook does not guarantee that it will run in a particular semester. The Student Handbook says minor courses are offered when at least 10 students register, although the Programme Chair may permit an exception.

- **Displayed source title:** `Minor_Courses_for_BTech_Students.xlsx · Design Minor minor; admission batch 2022`; the saved transcript does not show a separate Student Handbook citation for the ten-student rule.
- **Canonical source files:** https://github.com/goury-nandana/vu-academic-advisor-gai-a2/blob/main/VU_Minor_Data_Split.zip and https://github.com/goury-nandana/vu-academic-advisor-gai-a2/blob/main/4.%20Student%20Handbook%20Aug%202026.pdf
- **Model/date:** Model identifier not preserved in the saved transcript; transcript capture date 4 November 2026.
- **Accuracy / authority risk:** Medium. The minor names are sourced from the 2022 workbook section, but the ten-student rule was stated without a clearly displayed Handbook citation in this saved turn. That is an evidence-presentation defect even though the policy text exists in the supplied Handbook.
- **Copyright / attribution risk:** Low to medium. The output is a short factual summary of discipline names, not a copied sequence of course descriptions. The workbook's selection and arrangement may still be protected; do not redistribute the workbook or large portions of its rows without permission.
- **Corrective change:** The current route now retrieves the supporting Student Handbook passage alongside the minor workbook and adds a separate citation to the registration-threshold statement. If the Handbook passage is unavailable, the answer no longer states the ten-student rule as verified.
- **Recommended practice:** Cite each policy claim to the relevant Handbook, and each minor list to the matching batch-specific workbook section. State that actual offerings depend on the current registration list.

## Legal principles and ownership considerations

1. **Copyright protects expression, not bare facts or ideas.** A concise answer that restates course codes, credit values or programme names in the advisor's own format is different from reproducing full handbook pages, course descriptions, photographs, logos or tables.
2. **Compilations and databases can attract protection.** The Indian Copyright Act includes tables and compilations (including computer databases) in the definition of literary work. The fact that individual course codes and credit values are facts does not give permission to copy or republish the university's entire curated workbook.
3. **Computer-generated authorship needs careful treatment.** Section 2(d)(vi) of the Indian Copyright Act refers to the person who causes a computer-generated work to be created. Applying that provision to modern generative-AI workflows, and deciding whether a human has contributed enough original expression, can be fact-specific. This report does not declare that the model itself owns the output or that the student automatically owns everything.
4. **Provider terms do not settle VU/student ownership.** Groq's published Services Agreement addresses rights between Groq and its customer and places responsibility on the customer for having rights to the inputs it submits. That does not settle the separate contractual or institutional relationship between VU, a student, the project team and any third-party content owner.
5. **Permissions and consent matter.** Use university documents only within the permissions provided for the assignment or an authorised VU deployment. Obtain permission before using student-created work, images, recordings, identifiable transcripts or third-party materials in a public demo. Redact personal and student-identifying information.
6. **Prevent misleading attribution.** Do not imply that a generated answer is an official VU determination. Enrolment, eligibility, credit transfer, grades, exceptions and approvals remain decisions for the authorised university office.

## Safeguards adopted in the prototype

- Keep source links and source titles with answers where available.
- The prototype displays source titles/links for retrieved answers where available. A downloadable response-evidence export is **not implemented** in the current frontend; this review therefore relies on the saved transcript cited above, rather than claiming an app-generated evidence export.
- Warn users that uploads and profile details are sent to Groq for processing.
- Do not ask for Digiicampus passwords, student IDs or sensitive personal records.
- Treat retrieved pages and uploaded material as untrusted data; do not obey embedded instructions.
- Use synthetic profiles for the agent-workflow demonstration, not real student transcripts.

## References

- Government of India, Copyright Office, *The Copyright Act, 1957*, Chapter I, section 2(d)(vi): https://copyright.gov.in/Copyright_Act_1957/chapter_i.html
- Intellectual Property India, *Basics of Copyright*: https://ipindia.gov.in/basics-of-copyright
- India Code, *Copyright Act, 1957*, section 14: https://www.indiacode.nic.in/
- Groq, *Services Agreement* (customer data, input permissions and output responsibility): https://console.groq.com/docs/legal/services-agreement

**Review boundary:** This evaluation covers the three actual saved text answers above. It is not a general legal clearance for every future output, image, audio recording, university document or commercial deployment. VU should obtain its own legal and data-protection review before using real student data or distributing the system institution-wide.


## Synthetic-media scope and additional legal-risk analysis

**Scope distinction:** The three evidence samples reviewed above are actual text answers. They do not include an actual AI-generated image, audio clip, video, voice clone, or synthetic likeness. No legal conclusion about a particular media output is made here. This section records the risks and controls that should apply if multimodal generation is introduced in a later assignment phase.

| Media / use case | Principal copyright, consent, and misuse risks | Responsible-use controls |
|---|---|---|
| Generated infographic or image | Incorporating protected artwork, logos, photographs, or distinctive character designs; confusing users about university endorsement; unclear authorship/ownership of AI-generated expression | Prefer original diagrams based on factual course data; use only licensed or permissioned inputs; do not reproduce VU logos/third-party artwork absent permission; label AI-generated visuals; preserve prompt and source references when practical |
| Generated speech or audio | Unauthorized use of a person's voice, voice imitation, copyrighted music/recordings, or identifiable student voice data; misleading impersonation | Do not clone real people’s voices without informed consent and authorization; avoid copyrighted music; label synthetic speech; do not upload identifiable recordings unless purpose, consent, and access are documented |
| Generated video or likeness | Depiction of real students/faculty without consent, deceptive endorsements, manipulated statements, or derivative use of copyrighted footage | Use fictional/synthetic characters or explicitly consented participants; avoid portraying a real VU official as making an approval; disclose synthetic manipulation and restrict distribution |
| Student or university-supplied material as input | Uploading course notes, assessments, student projects, transcripts, images, or restricted handbook content beyond the permitted purpose | Confirm assignment or institutional permission; minimize and redact personal data; restrict access; honor provider retention and processing terms; do not assume possession equals permission |
| Reuse / publication of output | Output may resemble third-party expression; attribution may be incomplete; a generated result may contain factual error or create reputational confusion | Human-review before public or graded use; check similarity and sources; cite source material actually used; keep a record of prompt, output, tool/model and review; do not claim legal clearance based solely on AI generation |

### Ownership and licensing: practical position

- The Copyright Act, 1957, contains a computer-generated-work authorship provision in section 2(d)(vi), but its application to current generative AI systems and the required human contribution is not conclusively resolved by this project. Avoid categorical claims that an AI model owns the work or that a student automatically owns every output.
- Copyright or license rights in the input material remain distinct from rights, if any, in the generated output. Provider terms are not a substitute for permission from a university, student, photographer, author, performer, or other rights holder.
- Attribution is a transparency practice and may also be required by a license, assignment, or institutional policy; attribution alone does not cure unauthorized copying or use.
- A factual short text response can still create risk if it reproduces protected expression. Conversely, factual values such as course codes and credit counts are generally different from protected creative expression; compilation/database rights and restrictions still require consideration.
- These are risk-management conclusions for an academic prototype, not a legal opinion. Applicable institutional policy, contract terms, licenses, and facts may change the analysis.

### Evidence and review limitations

- The three output excerpts are transcribed from the saved conversation transcript identified in the opening statement. The repository report does not include a cryptographic hash or raw model response payload for that transcript.
- The model identifier and per-answer timestamps were not captured in the source transcript; they are expressly left unspecified.
- The review is a qualitative desk analysis. It did not perform similarity matching, image/audio forensic analysis, a license audit of every source, or legal clearance by VU counsel.
- This section is prospective guidance, not a claim that media-generation features are already implemented or that media outputs were tested.
