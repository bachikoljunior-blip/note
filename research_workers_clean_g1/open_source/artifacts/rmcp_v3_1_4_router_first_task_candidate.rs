//! Source-qualified refactor candidate for rmcp-v3.1.4.
//!
//! Exact upstream pin:
//! modelcontextprotocol/rust-sdk
//! 4a738b9dd99eaca418b614afa433a0cbdaf8d056
//!
//! STATUS: NOT COMPILED in this worker runtime (`cargo` is unavailable).
//! This candidate is intentionally narrow: it demonstrates how to leave
//! `ServerHandler::call_tool` absent so `#[tool_handler]` generates the
//! router-first implementation, while moving task materialization into the
//! registered tool after standard extractors and explicit pre-materialization
//! gates. Persistent create-or-get, restart redrive, and external-effect
//! idempotency/fencing are intentionally out of scope.

use rmcp::{
    ErrorData as McpError, ServerHandler,
    handler::server::{
        router::tool::ToolRouter,
        tool::{InputResponses as ToolInputResponses, RequestState},
        wrapper::Parameters,
    },
    model::{
        CallToolResponse, CallToolResult, ContentBlock, CreateTaskResult, GetTaskParams,
        GetTaskResult, InputRequiredResult, ServerCapabilities, ServerInfo, UpdateTaskParams,
        CancelTaskParams,
    },
    service::{RequestContext, RoleServer},
    task_manager::{TaskExit, TaskManager, TaskOptions},
    tool, tool_handler, tool_router,
};

#[derive(Debug, serde::Deserialize, rmcp::schemars::JsonSchema)]
pub struct SumArgs {
    pub a: i32,
    pub b: i32,
}

#[derive(Clone)]
struct TaskServer {
    tool_router: ToolRouter<TaskServer>,
    tasks: TaskManager,
}

fn request_state_is_valid(state: &str, _a: i32, _b: i32) -> bool {
    // Placeholder for server-authenticated requestState verification bound to
    // method/tool/arguments/principal/expiry. Raw requestState is not authority.
    state == "signed-op-placeholder"
}

fn current_policy_allows(_context: &RequestContext<RoleServer>) -> bool {
    // Placeholder for a fresh authorization/policy decision made before spawn.
    true
}

#[tool_router]
impl TaskServer {
    fn new() -> Self {
        Self {
            tool_router: Self::tool_router(),
            tasks: TaskManager::new(),
        }
    }

    #[tool(description = "Sum two numbers through the router-first task path")]
    async fn sum(
        &self,
        context: RequestContext<RoleServer>,
        Parameters(SumArgs { a, b }): Parameters<SumArgs>,
        RequestState(request_state): RequestState,
        ToolInputResponses(_input_responses): ToolInputResponses,
    ) -> Result<CallToolResponse, McpError> {
        // Gate 1: client Tasks capability BEFORE task materialization.
        let client_supports_tasks = context
            .client_capabilities()
            .is_some_and(|caps| caps.supports_tasks());
        if !client_supports_tasks {
            // A production policy can choose synchronous fallback instead.
            return Ok(CallToolResult::success(vec![ContentBlock::text(
                (a + b).to_string(),
            )])
            .into());
        }

        // Gate 2: side-effect-free MRTR/preflight round. No task exists yet.
        let Some(state) = request_state else {
            return Ok(InputRequiredResult::from_request_state(
                "signed-op-placeholder",
            )
            .into());
        };

        // Gate 3: continuation token and current policy must still be valid.
        if !request_state_is_valid(&state, a, b) {
            return Err(McpError::invalid_params("invalid request state", None));
        }
        if !current_policy_allows(&context) {
            return Err(McpError::invalid_params("policy denied", None));
        }

        // Only after ToolRouter route/disable lookup, standard Parameters
        // extraction, capability check, MRTR validation, and current policy do
        // we materialize a task.
        let task = self
            .tasks
            .spawn(TaskOptions::new().with_poll_interval_ms(10), move |ctx| {
                Box::pin(async move {
                    tokio::select! {
                        _ = ctx.cancelled() => Err(TaskExit::Cancelled),
                        _ = tokio::time::sleep(std::time::Duration::from_millis(50)) => {
                            Ok(CallToolResult::success(vec![ContentBlock::text(
                                (a + b).to_string(),
                            )]))
                        }
                    }
                })
            });
        Ok(CallToolResponse::Task(CreateTaskResult::new(task)))
    }
}

#[tool_handler]
impl ServerHandler for TaskServer {
    // Intentionally NO `call_tool` override. At exact rmcp-v3.1.4 the
    // `#[tool_handler]` macro generates ToolCallContext::new + ToolRouter.call.

    fn get_info(&self) -> ServerInfo {
        // The macro preserves a user-defined get_info(), so Tasks can still be
        // advertised while retaining its generated router-first call_tool().
        ServerInfo::new(
            ServerCapabilities::builder()
                .enable_tools()
                .enable_tasks()
                .build(),
        )
    }

    async fn get_task(
        &self,
        request: GetTaskParams,
        _context: RequestContext<RoleServer>,
    ) -> Result<GetTaskResult, McpError> {
        Ok(GetTaskResult::new(self.tasks.get_task(&request.task_id)?))
    }

    async fn update_task(
        &self,
        request: UpdateTaskParams,
        _context: RequestContext<RoleServer>,
    ) -> Result<(), McpError> {
        self.tasks
            .update_task(&request.task_id, request.input_responses)
    }

    async fn cancel_task(
        &self,
        request: CancelTaskParams,
        _context: RequestContext<RoleServer>,
    ) -> Result<(), McpError> {
        self.tasks.cancel_task(&request.task_id)
    }
}
