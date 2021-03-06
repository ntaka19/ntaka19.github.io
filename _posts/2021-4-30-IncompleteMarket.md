---
layout: post
title: Incomplete Markets
tags: 
- FE 
- Bjork
---

<script src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML" type="text/javascript"></script>

## Intro

Concept of (in)complete markets is discussed in different areas from different contexts.
Theoretical definition can be found in the Financial engineering area.(note that scope of defition may be narrower than that of other Econs area)


## Fundamental theorem of asset pricing

Before we go on to the definition, it is better to get concepts of "complete market" clearer. 
A quick way is to recap two fundamental theorems.


1.  The First Fundamental Theorem of Asset Pricing: A discrete market,
    on a discrete probability space
    $$(\Omega, \mathcal{F}, \mathcal{P})$$, is arbitrage-free if, and
    only if, there exists at least one risk neutral probability measure
    that is equivalent to the original probability measure, P.

2.  The Second Fundamental Theorem of Asset Pricing: An arbitrage-free
    market (S,B) consisting of a collection of stocks S and a risk-free
    bond B is complete if and only if there exists a unique risk-neutral
    measure that is equivalent to P and has numeraire B.

(wikipediaより抜粋．離散のケース）\
以下ではRisk neutral measure をmartingale measureとして置き換える。

## Complete marketの定義 (Chapter 8 P.119)

-   $$S=\left(S^{1}, \ldots, S^{N}\right)$$ : N traded risky assets.

-   We assume that all the underlying assets are traded on the market,
    but we do not assume that there exists an a priori market (or a
    price process) for the derivative.

-   \"If every contingent claim is reachable we say that the market is
    complete .\"

-   \"We say that a T-claim X can be replicated, alternatively that it
    is reachable or hedgeable, if there exists a self-financing
    portfolio h such that\" $$V_{T}^{h}=\mathcal{X}, \quad P-a . s$$

-   あとは上の関係を元に各時点のcontingent claimのpricingができる．

## Completeness-Absence of arbitrage 8.3 (P.125-126)

Let us consider a model with N traded underlying assets plus the risk
free asset (i.e. totally N +l assets). We assume that the price
processes of the underlying assets are driven by R \"random sources\".
We cannot give a precise definition of what constitutes a \"random
source\" here, but the typical example is a driving Wiener process.

If, for example, we have five independent Wiener processes driving our
prices, then R = 5.

#### Completeness and Arbitrage-free 

Completeness and absence of arbitrage work in opposite directions.
Fixed number of random sources $$R$$. 

-   Then every new underlying asset added to the model (without
    increasing R) will of course give us a potential opportunity of
    creating an arbitrage portfolio , so in order to have an arbitrage
    free market the number N of underlying assets must be small in
    comparison to the number of random sources R .

-   On the other hand we see that every new underlying asset added to
    the model gives us new possibilities of replicating a given
    contingent claim, so completeness requires N to be great in
    comparison to R.

#### Meta-theorem 8.3.1

\"Let N denote the number of underlying traded assets in the model
excluding the risk free asset, and let R denote the number of random
sources. Generically we then have the following relations:\"

1.  The model is arbitrage free if and only if $$N \leq R$$.

2.  The model is complete if and only if $$N \geq R$$

3.  The model is complete and arbitrage free if and only if N = R.

## Primer on incomplete markets (Chapter 9)

-   Model

    -   Observable stochastic process X, which is not assumed to be the
        price process of a traded asset. (eg. Temperature.
        $$d X_{t}=\mu\left(t, X_{t}\right) d t+\sigma\left(t, X_{t}\right) d W_{t}$$

    -   Consider a given contingent claim,
        $$\mathcal{Y}=\Phi\left(X_{T}\right)$$ Example,
        $$\Phi(x)=\left\{\begin{array}{cl}100, & \text { if } x \leq 20 \\ 0, & \text { if } x>20\end{array}\right.$$

    -   If, price of another derivative is given (=benchmark).
        $$\Gamma(x)=\left\{\begin{array}{cl}100, & \text { if } x \leq 25 \\ 0, & \text { if } x>25\end{array}\right.$$
        Then, we can price derivative $$\Phi$$. (Number of traded
        assets($$\Gamma$$(x)) = 1, Number of random sources=1)

-   Summary:

    -   In an incomplete market requirement of no arbitrage is no longer
        sufficient to determine a unique price for the derivative.

    -   No arbitrage pricing can be done by applying same martingale
        measure.

    -   When dealing with derivative pricing in an incomplete market, we
        need to fix a specific martingale measure . (market chooses the
        martingale measure)
        (無数にマルチンゲール測度が存在しうるとSecond fundamental
        theoremによりincomplete.)
