# Final Project for CS252R: Advanced Topics in Programming Languages

## Author 

Andrew Sima

## Abstract 

This project studies methods for optimizing boolean circuits in the context of fully homomorphic encryption (FHE). With respect to encrypted computation and securing machine learning, the complexity of FHE and lack of standardized programming paradigms remain challenges in its integration into applications. One solution to this is an FHE compiler—a toolchain converting high-level languages into an intermediate representation respecting a chosen FHE encryption scheme. However, computational overhead remains a hurdle, prompting exploration into optimizing boolean circuits via tools like the ABC toolchain and logic gate rearrangement techniques. Following methods from the literature, we are able to replicate state-of-the-art program synthesis-based circuit optimization systems, with comparable metrics to the best reported benchmarks.

## Quickstart

```bash
python test.py
```