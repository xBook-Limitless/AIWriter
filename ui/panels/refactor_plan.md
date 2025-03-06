# 世界观面板 (WorldViewPanel) 重构计划

## 文件结构组织

代码将按照以下结构重新组织:

1. **总框架部分** - 初始化、UI创建、步骤导航等基础功能
   - `__init__`
   - `create_widgets`
   - `_create_linear_outline_system`
   - `update_step_view`
   - `_navigate_prev`
   - `_navigate_next`
   - 其他基础UI方法

2. **步骤1: 构建基础模板** - 模板创建、预览、AI生成等
   - `_create_base_template`
   - `_create_template_selection`
   - `_display_template_preview`
   - `_generate_template_preview`
   - `_select_template`
   - `_ai_generate_template`

3. **步骤2: 模板参数调整** - 参数提取、编辑、保存等
   - `_create_parameter_input_view`
   - `_extract_parameters_from_template`
   - `_save_parameters`
   - `_update_parameter_preview`

4. **步骤3: 生成扩展建议** - 建议生成和展示
   - `_create_suggestion_generation`
   - `_generate_suggestions`
   - `_show_generated_suggestions`
   - `_save_suggestions`

5. **步骤4: 检测核心冲突** - 冲突检测和处理
   - `_create_conflict_detection`
   - `_detect_conflicts`
   - `_display_conflicts`
   - `_confirm_conflicts`

6. **步骤5: 完善世界完整度** - 完整性验证和优化
   - `_create_completion_validation`
   - `_validate_completeness`
   - `_optimize_completeness`
   - `_save_completion_data`

7. **步骤6: 优化风格一致性** - 风格设置和预览
   - `_create_style_polishing`
   - `_polish_style`
   - `_refresh_style_preview`
   - `_save_style_data`

8. **步骤7: 世界观展示** - 最终展示和导出
   - `_create_world_view_display`
   - `_generate_final_view`
   - `_display_final_view`
   - `_finalize_worldview`

9. **通用功能** - 文件保存等通用方法
   - `_save_to_file`
   - `_load_config`
   - 其他辅助方法

## 重构步骤

1. 备份原始文件
2. 创建重构计划文档（本文档）
3. 在代码中添加分隔注释，标记各个部分
4. 按照新结构重新组织代码
5. 测试确保功能正常

## 重要注意事项

- 保持内部逻辑不变
- 确保所有导入和类定义保持不变
- 添加清晰的注释标记每个部分的开始和结束
- 确保方法之间的调用关系保持正确 