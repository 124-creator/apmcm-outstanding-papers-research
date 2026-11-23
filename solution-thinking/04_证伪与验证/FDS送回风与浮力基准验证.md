# FDS 送回风与浮力基准验证

- 阶段时刻：2026-11-20 14:29:01 预登记冻结，14:29:05 起跑，约 14:34:56 编排脚本结束，随后完成评分窗口更正、估时订正与本报告（Asia/Shanghai，UTC+8）。
- 机器：DESKTOP-N9NN2UK（machineId `364b441a-d3dc-475a-b2e7-8d7ac599d7a2`）。
- 工作目录：`C:\Users\Admin\参加数学建模比赛\APMCM_2024B_解题与思考\apmcm-2024b-solution`。
- 求解器：本机已有用户级解压的官方 `FDS-6.11.2-0-g8e4c2c4-release`（路径 `tools\fds\FDS-6.11.2_SMV-6.11.3\firemodels\FDS6\bin\fds.exe`）。Python 3.12.10：`C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe`。未修改系统 PATH/防火墙，未提权，未新装大型软件，未换题，未检索本题题解或获奖论文，未启动完整冬夏本题，未优化外形，未调旧射流闭合。
- 产物目录：`results/fds_room_verification/`。上一阶段固体导热验证 `results/fds_first_verification/` 与 `FDS安装与首个验证记录.md` 全部保留。ht3d_slab **不得**冒充本轮房间场验证。

## 1. 结论（先看这里）

本轮实际覆盖了三类过程，层次必须分开写：

1. **Verification（数值求解正确，不是房间实验）**：官方 `HVAC_mass_conservation` 与本轮 20³→40³ 空间细化，以及官方 `HVAC_mass_transport_energy`。送回风管道的质量守恒与能量/压差输送，在官方容差 0.01 下通过。质量终点相对误差约为 1.74×10⁻⁵（组分 1）与 0（总质量）；细化网格为 2.10×10⁻⁵ 与 0，不是粗网格偶然过关。能量在官方 dataplot 窗口 t∈[20,40] s 上，焓的平均相对误差 6.51×10⁻⁷，压差 5.96×10⁻⁴，均远小于 0.01。这些算例是约 1 m 量级、给定体积流量或短管损失的小箱体，不能外推为本题 8 m/s 柜式射流或人员区温场。
2. **与工程关联式比较（官方无数值通过阈值）**：官方 `nat_conv_hot_plate` 算例 1，网格 8 与 16，开域热板自然对流，Pr=1，Ra≈1.890×10⁸，ΔT=210 K。按官方脚本最后一行热流换算 Nu：向下表面相对 Incropera & DeWitt 关联式误差为 1.19%（网格 8）与 6.87%（网格 16）；向上表面为 5.46% 与 7.54%。两侧热流方向正确（离开热面）。官方没有 Error_Tolerance。加密后误差并未变小，向上表面在粗网格上仍有晚期振荡，故这是数量级与方向正确的对照，不是“湍流房间已验证”，也不是封闭房间或空气 Pr≈0.7 的房间自然对流。
3. **Validation（房间混合通风实验）未完成本轮**：最接近且数据完备的官方房间送回风实验是 Restivo 1979（与此前已见的 IEA Annex 20 2D1 同属 Nielsen/Restivo 缝口通风房间家族，不是盲测）。官方输入约 995,328 单元、T_END=900 s。本轮的 T_END=5 s 估时输入把 `T_END=900.` 误写成非法的 `T_END=5.0.`，FDS 报 ERROR(101) 后以退出码 0 结束且无 `.out`，编排脚本误判为 0.28 分钟并错误启动了官方 900 s 串行计算。随后用该次真实推进作估时：从 14:33:43 到 14:34:50（Asia/Shanghai）模拟到 t=2.147 s（第 60 步），墙钟 67 s，线性外推官方 900 s 约 **7.80 小时（约 468 分钟）**；即便按 3 个 MPI 进程理想线性加速，下界仍约 156 分钟，远超预登记约 15 分钟预算。该串行作业（仅本阶段启动的 `fds.exe` PID 29124）已停止，日志与部分 `.out` 保留。**Restivo 不算通过，也不得把未稳态短跑当作通过。**

**对本题外推仍不支持的关键缺口**：柜式紧凑射流（题面约 8 m/s，几何与 Re 均远高于 Restivo 缝口 Re≈5.1×10³）；封闭房间内送回风与热浮力耦合的冬夏人员区温场；湍流房间回流速度场的实验对照（Restivo 未跑完）；空气 Pr≈0.7 的房间尺度自然对流；辐射/人体/家具耦合；外形排名。

**能否开始一个非排名的本题先导模拟**：可以，但只作为摸清网格、边界与冬夏浮力耦合工作流的**非排名、非验收**先导，不得声称房间送回风速度场或冬夏人员区温场已经得到实验级验证，更不得据此优化或排名外形。若下一步要补上房间场实验对照，需要单独批准数小时量级的官方 Restivo（建议官方 3 进程）或其它明确缩小但仍有意义的官方房间算例，而不是在本轮预算里偷偷跑完。本轮到此停止，不启动冬夏本题。

## 2. Verification 与 Validation 的区分

- Verification：把离散方程的数值解与官方理想/解析目标比较，证明安装与格式在该路径上算对。本轮 HVAC 质量与能量属于这一层。
- Validation：把预测与独立实验或官方采用的工程关联式比较。Restivo 是实验 Validation，但未完成；热板是与关联式比较，官方明确无数值通过阈值，且不是封闭房间实验。
- 若只完成解析层流或小箱体守恒，不能称湍流房间已验证。本轮没有完成房间实验对照，因此不做该声明。
- 不用火灾羽流或带火能量收支冒充 8 m/s 空调紧凑射流。本轮未跑任何火源算例。

## 3. 预登记（运行前已冻结，未改阈值、未为过关改物理）

冻结文件（2026-11-20T14:29:01+08:00，任何本阶段 FDS 运行之前写入，本轮未覆盖）：

- `results/fds_room_verification/registered_parameters.json`
- `results/fds_room_verification/参数预登记.md`

预登记要点：最多 4 个 MPI/线程，小算例串行；评分算例预算约 15 分钟；空间或时间细化至少一项；记录误差与守恒而不只看退出码；官方输入不得为拟合验收结果而改；预登记指标不合适须透明修订并承认探索性。

一项实现更正（不是改官方阈值，也不是调参）：预登记正确引用了官方 dataplot 的 Quantity=Relative Error、Metric=mean、容差 0.01，但漏抄 `d2_Comp_Start=20`、`d2_Comp_End=40`。首次实现用全部 DEVC 样本（含 t=0 时 ΔP=0 与启动振荡）做平均，压差相对误差 2.77%，看起来“未通过”。官方窗口 t∈[20,40] s 上压差平均相对误差为 5.96×10⁻⁴，通过 0.01。摘录见 `official_sources/from_github_tag_FDS-6.11.2/FDS_verification_dataplot_inputs_HVAC_excerpt.csv`。两种窗口的数字都保留在 `csv/hvac_energy_errors.csv` 与 `metrics_official_window_addendum.json`，不把首次实现的窗口误差伪装成预登记失败，也不隐瞒更正过程。

## 4. 环境、命令与资源

- 版本：所有完成算例的 `*_git.txt` 与 `.out` 均为 `FDS-6.11.2-0-g8e4c2c4-release`。`fds -v` stderr 同期记录于 `logs/fds_version.stderr.txt`。Intel MPI 2021.16；本轮完成算例均为 1 个 MPI 进程、`OMP_NUM_THREADS=1`。
- 调用方式：会话环境内直接调用上述 `fds.exe`，不改系统 PATH。Restivo 估时曾用捆绑 `fds_local -p 3 -o 1`，三个 MPI 进程确实在本机启动，说明 3 进程环境可用；失败原因是 TIME 行非法，不是 MPI 不可用。
- 墙钟（.out 内 Total Elapsed Wall Clock Time，Asia/Shanghai 起始时刻）：
  - HVAC_mass_conservation：8000 单元，T_END=10 s，14:29:15 起，9.116 s，`STOP: FDS completed successfully`。
  - HVAC_mass_conservation_dx2：64000 单元，T_END=10 s，14:29:25 起，148.307 s，成功。细化变慢是因为 Δx 减半、时间步变小，属于正常代价，仍在 15 分钟内。
  - HVAC_mass_transport_energy：1100 单元，T_END=40 s，14:31:53 起，3.671 s，成功。
  - nat_conv_hot_plate_1_8：4096 单元（8 个网格由 MULT 生成，串行一个进程），T_END=100 s，14:31:57 起，10.384 s，成功。
  - nat_conv_hot_plate_1_16：32768 单元，T_END=100 s，14:32:07 起，95.195 s，成功。未跑官方 32 档（16 档已近 2 分钟，32 档预计更长，预登记为仅在 16 档明显低于预算时才考虑）。
  - Restivo 官方 900 s：误启动后于约 73 s 墙钟被停止，见第 7 节。
- 命令与日志：`logs/run_*.stderr.txt`、`run_facts.json`。完整编排日志不替代各算例 `.out`。

## 5. 算例选择、几何与适用区间

官方指南与 Validation 目录中，短而数据完备、且直接针对送回风质量/能量守恒的标准 Verification 是 HVAC 质量与能量输送算例（来自已校验 Windows 安装包 `Examples/HVAC`）。非等温有界/自然对流方面，官方 `nat_conv_hot_plate` 有网格序列与脚本化关联式，可在分钟级跑完。房间混合通风实验优先 Restivo 1979（Validation Guide 的 Compartment Air Flow Experiment），但完整官方输入超出本轮时间预算，见第 7 节。没有再无限搜索其它房间实验。

|算例|层次|几何与边界|无量纲与适用区间|本轮角色|
|---|---|---|---|---|
|HVAC_mass_conservation|Verification|1 m 立方体；两路给定 VOLUME_FLOW=0.1 m³/s、AREA=0.1 m² 的对侧送回风（风口 0.2 m×0.2 m，体积平均出流约 2.5 m/s）；STRATIFICATION=F，无辐射|无浮力（Ri 不进入）；目的是管道质量守恒，不是射流混合|官方质量守恒 + 本轮网格细化|
|HVAC_mass_transport_energy|Verification|两间 0.5 m×1 m×1 m 房间，0.1 m 隔墙，左室初温 100 °C；DUCT1 给定 0.1 m³/s 且 N_CELLS=10，DUCT2 由 LOSS=2 驱动；官方理想焓 293.15、ΔP=0.8928 Pa|小箱体能量/压差输送 Verification，不是房间射流|官方能量/压差|
|nat_conv_hot_plate 算例 1|与关联式比较|开域，8 个 1 m 立方网格；两块 1 m×1 m 热板（下表面朝下、上表面朝上），TMP_FRONT=230 °C，OPEN 边界|Pr=1 的 LJ AIR（不是空气 Pr≈0.7）；ΔT=210 K；特征长度 L=S/4=0.25 m；Ra≈1.890×10⁸（向上板进入 Ra>10⁷ 的 1/3 次关联式区间）|官方网格 8、16|
|Restivo 1979|Validation（未完成）|9 m×3 m×3 m；顶缝送风 VEL=0.455 m/s，缝高 0.168 m（z=2.832–3.0 m）、全宽 3 m；对侧近地 OPEN 开口高 0.48 m；等温，RADIATION=F|Re_slot≈U h/ν≈0.455×0.168/1.5×10⁻⁵≈5.1×10³（弱湍流缝口射流）；Ri≈0；不是 8 m/s 柜式紧凑射流，也不验证热浮力|最接近的官方房间混合通风实验；本轮仅有估时与被停止的部分推进|

此前壁面射流阶段已使用 IEA Annex 20 2D1。该二维数据与 Restivo 同属缝口通风房间家族。即使将来跑完 Restivo，也必须披露：这不是对该类房间实验的盲测。FDS 本身在本项目中此前未跑过 Restivo。旧经验射流闭合本轮未改、未重跑。

## 6. 结果与误差（不是只看退出成功）

### 6.1 HVAC 质量守恒（Verification，官方 metric=end，容差 0.01）

官方理想值恒为 Ideal Species 1=0.5819961 kg、Ideal Total=1.1639922 kg。

|算例|网格|FDS Species 1 终点|相对误差|FDS Total 终点|相对误差|判定|
|---|---|---|---|---|---|---|
|官方|20³=8000|0.58198598|1.739×10⁻⁵|1.1639922|0|通过|
|本轮细化|40³=64000|0.5819839|2.096×10⁻⁵|1.1639922|0|通过|

总质量在全部输出时刻与理想值一致（CSV 中为 1.1639922）。组分 1 仅有 10⁻⁵ 量级漂移，细化后同量级且仍远小于 1%。空间细化排除了“粗网格碰巧过关”的解释。过程曲线见已有 `figures/hvac_mass_conservation.png`，数值见 `csv/hvac_mass_errors.csv` 与各工作目录 `*_devc.csv`。

这只证明本安装在该 HVAC 质量输送路径上与官方理想目标一致，不证明房间湍流混合正确。

### 6.2 HVAC 能量与压差（Verification，官方 metric=mean，窗口 [20,40] s，容差 0.01）

官方理想焓 293.15、理想 ΔP=0.8928 Pa。启动阶段 ΔP 从 0 跳到约 3.76 Pa 再变号，t≈8–10 s 后进入约 0.89–0.90 Pa 的平台。

|窗口|焓平均相对误差|ΔP 平均相对误差|若用 0.01 判断|
|---|---|---|---|
|全部样本含 t=0（首次实现，非正式窗口）|2.490×10⁻⁵|2.775×10⁻²|焓过、压差不过|
|官方 d2_Comp_Start/End = 20–40 s|6.512×10⁻⁷|5.962×10⁻⁴|全部通过|
|仅终点（探索性，非正式）|3.514×10⁻⁶|2.412×10⁻³|全部低于 0.01|

按引用的官方 dataplot 定义，本算例通过。首次实现漏窗口的数字予以保留，以免只展示“通过”后的窗口。曲线见 `figures/hvac_enthalpy.png`、`figures/hvac_delta_p.png` 及原 `figures/hvac_mass_transport_energy.png`。

几何仍是短管小箱，不能外推柜式空调射流。

### 6.3 开域热板自然对流（关联式对照，无官方数值阈值）

官方脚本常数：g=9.80665，MW=28.85476，μ=1.8216×10⁻⁵，k=0.018216，cp=1000，T1=503 K，T2=293 K，L=S/4。由此 Ra=1.88966402×10⁸。向下 Nu_corr=0.52 Ra^0.2=23.5115；向上因 Ra>10⁷，Nu_corr=0.15 Ra^0.3333333333333333=86.0768（官方绘图曲线用指数 0.333，值为 85.5317，差别很小；本轮主表跟随脚本注释与预登记的 1/3 次）。Nu 由最后一行 DEVC 热流按官方公式换算。

|网格|单元|Nu_FDS 下 / 关联式|相对误差|Nu_FDS 上 / 关联式|相对误差|热流离开热面|t≥80 s 向上热流变化（kW）|
|---|---|---|---|---|---|---|---|
|8|4096|23.231 / 23.511|1.192%|81.375 / 86.077|5.462%|是 / 是|1.228–1.322（仍振荡）|
|16|32768|21.896 / 23.511|6.872%|79.589 / 86.077|7.537%|是 / 是|1.213–1.222（较稳）|

加密并未更接近关联式。向下表面在两套网格上晚期都已较稳；向上表面网格 8 在 t=100 s 仍有明显振荡，因此“最后一行”本身带采样波动。关联式也有经验不确定性。本轮把上述误差如实报告，**不设事后通过线，不宣称官方 Validation 通过**。图：`figures/nat_conv_qdot_down.png`、`figures/nat_conv_qdot_up.png`、`figures/nat_conv_nusselt.png`。

适用界限：开域、Pr=1、大温差热板，不是封闭居室，不是送回风射流，不是本题冬夏小温差人员区。

### 6.4 Restivo 房间实验（未完成，不给通过）

见下一节。没有实验速度 RMSE，没有结构符号判定，没有官方图对照。

## 7. Restivo 估时失败、误启动与预算停止

1. 预登记要求：先把官方 `Restivo.fds` 只改 CHID 与 T_END=5 s 做估时，短跑不作通过依据；若外推超过约 15 分钟，则不启动 900 s。
2. 实际写入的估时输入是 `&TIME T_END=5.0. /`（脚本 `f"T_END={t_end}."` 在 t_end=5.0 时多了一个小数点）。该文件保留在 `work/Restivo_timing/Restivo_timing.fds`，修改说明在 `MODIFICATIONS.txt`。
3. `fds_local -p 3 -o 1 Restivo_timing.fds` 在 0.176 s 内退出码 0，stderr 为 `ERROR(101): Problem with TIME line`，无 `.out`。随后串行 `fds.exe` 0.094 s，同样 ERROR(101)。编排脚本把“无 .out 且 rc=0”误当成成功，按 0.09 s×900/5 得到 **0.28 分钟** 的虚假估时，并启动了官方 `Restivo.fds` 的串行计算。
4. 官方输入本身被原样复制（SHA 与 `official_sources/from_github_tag_FDS-6.11.2/Restivo.fds` 一致），T_END=900，995,328 单元，3 个网格在同一个串行进程里。`.out` 起始时间为 2026-11-20 14:33:43（Asia/Shanghai）。串行还出现 `WARNING: DEVC u_left is not within any mesh` 与 `u_right` 同样警告（测点在 x=3 m 与 6 m 的网格界面上）。官方打算用 `-p 3`；即使将来重跑，也应使用官方 3 进程，而不是这个串行作业。
5. 真实推进（`work/Restivo/Restivo.out` 与 `logs/Restivo_partial_before_stop.out`）：第 30 步 14:34:18，t=1.105 s；最后完整记录第 60 步 14:34:50，t=2.14730 s，墙钟 67 s。外推 T_END=900 s：900/2.14730×67 ≈ **28080 s ≈ 7.80 小时 ≈ 468 分钟**。3 进程理想线性下界仍约 156 分钟，都远大于 15 分钟。
6. 因此在 14:34:44 左右结束了仅由本阶段启动的 `fds.exe` PID 29124（内存约 1.0 GB，属该作业）。这是预算纠正，不是结束无关进程。停止说明：`logs/Restivo_full_stopped.txt`。编排脚本记录该次返回码 1、墙钟 73.251 s、`scored=false`。
7. 本轮不再启动官方 900 s，也不再为“补一个短而宣称通过”的未稳态房间场去改 T_END。估时证据已经足够说明：完整官方 Restivo 不适合本轮 15 分钟预算。剩余缺口明确保留：本题最接近的官方房间混合通风实验存在且数据完备，但尚未在本机跑完，等温速度场仍未得到实验对照。

## 8. 落盘与完整性

- 官方源：安装包内 HVAC 输入与理想 CSV；GitHub 标签 `FDS-6.11.2` 的 Restivo 与热板输入及 `nat_conv_hot_plate.py`；`firemodels/exp` 的 `Restivo.csv`（本轮因未完成实验对照而未用于评分，文件已保存）。
- 工作副本：官方算例输入 SHA 与官方源一致；仅 `HVAC_mass_conservation_dx2`（IJK 与 CHID）和非法 TIME 的 `Restivo_timing` 是预登记允许的修改，并留有 `MODIFICATIONS.txt`。
- 预登记文件未被覆盖。ht3d 目录与 `FDS安装与首个验证记录.md` 仍在。
- 核验表：`results/fds_room_verification/disk_verification.md` 与 `disk_verification.json`（全部检查通过：True）。
- 指标与事实：`metrics.json`（含官方窗口更正）、`metrics_official_window_addendum.json`、`run_facts.json`（保留首次错误估时）、`run_facts_restivo_timing_correction.json`、`csv/*.csv`、`figures/*.png`（常规折线/柱状图，非生成式配图）、各 `work/*/ *.out` 与 `*_devc.csv`。

## 9. 对本题的含义与先导模拟决策

已支持的陈述：

- 本机官方 FDS 6.11.2 安装能在官方 HVAC 送回风质量守恒与能量/压差输送 Verification 上达到官方 1% 容差，细化后质量守恒仍然成立。
- 开域非等温浮力换热在官方热板算例上给出正确热流方向，Nu 与常用关联式相差约 1–8%，可作为浮力模块的粗检查，不是房间验收。
- 固体导热 ht3d_slab（上一阶段，终点相对误差 2.622×10⁻⁴）仍然只是固体导热。

明确不能说的话：

- 不能说湍流房间送回风已被验证。
- 不能说 8 m/s 柜式紧凑射流已被验证（Restivo 缝口约 0.455 m/s、Re≈5×10³，且未跑完）。
- 不能说冬夏人员区温场已被验证（无封闭房间非等温实验对照，热板也不是居室条件）。
- 不能把 Annex 20 / Restivo 家族写成盲测。

**决策：可以开始一个非排名、只用于摸清本题房间网格/边界/冬夏浮力耦合流程的先导模拟；不可以把它当作已通过的空间场验收，不可以进入外形优化或排名。** 先导若做，应使用温和资源，预先冻结短时间与粗网格，并在报告中重复上述缺口。完整冬夏本题与外形优化本轮明确不启动。

本报告写完即停止。
