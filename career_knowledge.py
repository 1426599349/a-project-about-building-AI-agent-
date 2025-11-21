# career_knowledge.py - 精简职业规划知识库
CAREER_KNOWLEDGE = {
    "简历优化": {
        "STAR法则": "情境(Situation)-任务(Task)-行动(Action)-结果(Result)。例如：'在用户流失率高的情境下，我负责优化注册流程，通过A/B测试和用户访谈，最终将转化率提升了25%'",
        "量化成果": "用数据说话：'优化了系统性能' → '通过缓存优化，将API响应时间从500ms降低到200ms'",
        "技术栈突出": "针对技术岗位：明确列出技术栈，描述在项目中如何应用这些技术解决实际问题",
        "关键词匹配": "分析招聘要求，在简历中使用相同的关键词，确保通过ATS系统筛选"
    },
    
    "面试准备": {
        "案例准备": "准备3-5个深度案例，每个案例包含：背景、你的角色、具体行动、量化结果、经验总结",
        "公司研究": "深入研究目标公司：产品特点、商业模式、竞品分析、最新动态、企业文化",
        "行为问题": "使用STAR结构回答：情境(20%)-任务(10%)-行动(40%)-结果(30%)，重点突出你的贡献",
        "技术面试": "技术岗位：刷题准备+系统设计+项目深度讨论；产品岗位：产品设计+数据分析+商业思维"
    },
    
    "职业规划": {
        "目标设定": "SMART原则：具体(Specific)、可衡量(Measurable)、可实现(Achievable)、相关(Relevant)、有时限(Time-bound)",
        "技能地图": "分析目标岗位所需技能 vs 当前技能，找出差距，制定学习路径",
        "学习计划": "将大目标分解为小任务：'学习Python' → '3个月完成基础语法→2个月完成数据分析项目→1个月完成实战项目'",
        "职业路径": "技术路线：初级→高级→架构师/技术专家；管理路线：技术→组长→经理→总监；产品路线：助理→产品→高级→总监"
    },
    
    "薪资谈判": {
        "市场调研": "使用拉勾、BOSS直聘、Levels.fyi等平台了解薪资范围，考虑公司规模、地域、经验要求",
        "价值主张": "准备你的价值清单：技术能力、项目成果、业务贡献、团队影响、特殊技能",
        "谈判时机": "在对方明确想要你之后谈判，避免过早讨论具体数字，先了解薪资结构",
        "整体薪酬": "考虑基本工资、奖金、股票、福利、培训机会、工作生活平衡等综合因素"
    }
}

def get_relevant_knowledge(user_input):
    """根据用户输入获取相关知识"""
    input_lower = user_input.lower()
    relevant_knowledge = []
    
    # 简单关键词匹配
    if any(word in input_lower for word in ["简历", "cv", "求职信"]):
        relevant_knowledge.append("简历优化知识：")
        relevant_knowledge.extend([f"- {key}: {value}" for key, value in CAREER_KNOWLEDGE["简历优化"].items()])
    
    if any(word in input_lower for word in ["面试", "面经", "interview"]):
        relevant_knowledge.append("面试准备知识：")
        relevant_knowledge.extend([f"- {key}: {value}" for key, value in CAREER_KNOWLEDGE["面试准备"].items()])
    
    if any(word in input_lower for word in ["职业", "规划", "发展", "转行"]):
        relevant_knowledge.append("职业规划知识：")
        relevant_knowledge.extend([f"- {key}: {value}" for key, value in CAREER_KNOWLEDGE["职业规划"].items()])
    
    if any(word in input_lower for word in ["薪资", "工资", "谈薪", "待遇"]):
        relevant_knowledge.append("薪资谈判知识：")
        relevant_knowledge.extend([f"- {key}: {value}" for key, value in CAREER_KNOWLEDGE["薪资谈判"].items()])
    
    return "\n".join(relevant_knowledge) if relevant_knowledge else None

def enhance_prompt(user_input):
    """用知识库增强用户问题"""
    knowledge = get_relevant_knowledge(user_input)
    
    if not knowledge:
        return user_input  # 没有相关知识，返回原问题
    
    enhanced_prompt = f"""请基于以下职业规划专业知识来回答问题：

{knowledge}

用户问题：{user_input}

请结合以上专业知识，给出具体、可操作的建议，避免泛泛而谈。"""
    
    return enhanced_prompt