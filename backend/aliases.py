from backend.entity.embedder import Modality

Version = str
Dataset = str
Collection = tuple[Dataset, Version]

Score = float
Path = str
Candidate = tuple[Path, Score, Modality]
CandidateWithCollection = tuple[Candidate, Collection]
