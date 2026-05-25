### Summary

We form the program as a single linear goal program with the following objectives in order of priority

1. Minimize the number of active servers used
2. Minimize resource stranding across servers

### Parameters

* For each VM $i$
  * $c_i$: CPU requirement
  * $m_i$: memory requirement
  * $d_i$: disk requirement
* For each server $j$
  * $C_j$: CPU capacity
  * $M_j$: memory capacity
  * $D_j$: disk capacity
* $V$: number of VMs
* $S$: number of servers

### Decision Variables

$$
\begin{align*}

x_{ij} &= \begin{cases}
  1 \quad \text{if VM $i$ is placed on server $j$} \\
  0 \quad \text{otherwise}
\end{cases}

\\
\\

y_{j} &= \begin{cases}
  1 \quad \text{if server $j$ is active} \\
  0 \quad \text{otherwise}
\end{cases}

\end{align*}
$$

### Constraints

Each VM is assigned to exactly one server

$$
\begin{align*}
\sum_{j=1}^{S}{x_{ij}} = 1 \quad \forall{i}
\end{align*}
$$

Capacity of each server is respected
$$
\begin{align*}
\text{CPU:} 		& \quad \sum_{i=1}^{V}{c_i x_{ij}} \le C_j y_j \quad \forall{j} \\
\text{Memory:} 	& \quad \sum_{i=1}^{V}{m_i x_{ij}} \le M_j y_j \quad \forall{j} \\
\text{Disk:} 		& \quad \sum_{i=1}^{V}{d_i x_{ij}} \le D_j y_j \quad \forall{j}
\end{align*}
$$

### Priority 1: Minimize Servers

$$
\begin{align*}
\text{Minimize } \quad \sum_{j=1}^Sy_j
\end{align*}
$$

### Priority 2: Minimize Stranding

A resource is "stranded" if one resource on a server is exhaused while others remain unused. To model this, we will be measuring the proportion of unused CPU, memory, and disk on each server and then using the difference between the minimum and maximum of unused resources on a server. This will give a reasonable proxy for balance. Here is an example:

|Remaining CPU|Remaining Memory|Remaining Disk|Difference|
|-|-|-|-|
|$0.2$|$0.25$|$0.30$|$0.3-0.2=0.10$|
|$0.05$|$0.30$|$0.80$|$0.8-0.05=0.75$|

In this case, a difference $0.1$ indicates a better balanced and more desirable VM placements.

We define $u_j$ as the amount of unused resources on server $j$

$$
\begin{align*}

u_j^{cpu} &= C_j y_j - \sum_{i=1}^{v}c_ix_{ij}
\\
u_j^{mem} &= M_j y_j - \sum_{i=1}^{v}m_ix_{ij}
\\
u_j^{disk} &= D_j y_j - \sum_{i=1}^{v}d_ix_{ij}

\end{align*}
$$

We can then define $r_j$ as the proportion (i.e. normalized) of unused resources on server $j$
$$
\begin{align*}
r_j^{cpu} &= \frac{u_j^{cpu}}{C_j}
\\
r_j^{mem} &= \frac{u_j^{mem}}{M_j}
\\
r_j^{disk} &= \frac{u_j^{disk}}{D_j}
\end{align*}
$$

Maximum and minimium unused resources $z_j$ for server $j$ can be defined as

$$
\begin{align*}

z_j^{max} &\ge r_j^{cpu} 	\quad & z_j^{min} &\le r_j^{cpu} \\
z_j^{max} &\ge r_j^{mem} 	\quad & z_j^{min} &\le r_j^{mem} \\
z_j^{max} &\ge r_j^{disk} \quad & z_j^{min} &\le r_j^{disk} \\

\end{align*}
$$

The objective function is then
$$
\begin{align*}
\text{Minimize} \quad \sum_{j=1}^{S}(z_j^{max} - z_j^{min})
\end{align*}
$$
