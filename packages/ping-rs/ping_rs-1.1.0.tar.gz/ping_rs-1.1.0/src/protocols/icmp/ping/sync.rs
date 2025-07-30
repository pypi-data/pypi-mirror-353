use crate::protocols::icmp::platform;
use crate::types::result::PingResult;
use crate::utils::conversion::{create_ping_options, extract_target};
use crate::utils::validation::{validate_interval_ms, validate_timeout_ms};
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;

/// Python 包装的 Pinger 类
#[pyclass]
pub struct Pinger {
    target: String,
    interval_ms: u64,
    interface: Option<String>,
    ipv4: bool,
    ipv6: bool,
}

#[pymethods]
impl Pinger {
    #[new]
    #[pyo3(signature = (target, interval_ms=1000, interface=None, ipv4=false, ipv6=false))]
    pub fn new(
        target: &Bound<PyAny>,
        interval_ms: i64,
        interface: Option<String>,
        ipv4: bool,
        ipv6: bool,
    ) -> PyResult<Self> {
        let target_str = extract_target(target)?;

        // 验证 interval_ms 参数
        let interval_ms_u64 = validate_interval_ms(interval_ms, "interval_ms")?;

        Ok(Self {
            target: target_str,
            interval_ms: interval_ms_u64,
            interface,
            ipv4,
            ipv6,
        })
    }

    /// 同步执行单次 ping
    pub fn ping_once(&self) -> PyResult<PingResult> {
        let options = create_ping_options(
            &self.target,
            self.interval_ms,
            self.interface.clone(),
            self.ipv4,
            self.ipv6,
        );

        // 执行ping并等待第一个结果
        let receiver = platform::execute_ping(options)
            .map_err(|e| PyErr::new::<PyRuntimeError, _>(format!("Failed to start ping: {}", e)))?;

        // 等待第一个结果
        match receiver.recv() {
            Ok(result) => Ok(result.into()),
            Err(_) => Err(PyErr::new::<PyRuntimeError, _>("Failed to receive ping result")),
        }
    }

    /// 同步执行多次 ping
    #[pyo3(signature = (count=4, timeout_ms=None))]
    pub fn ping_multiple(&self, count: i32, timeout_ms: Option<i64>) -> PyResult<Vec<PingResult>> {
        // 验证 count 参数
        let count = crate::utils::validation::validate_count(count, "count")?;

        // 验证 timeout_ms 参数
        let timeout = validate_timeout_ms(timeout_ms, self.interval_ms, "timeout_ms")?;

        let options = create_ping_options(
            &self.target,
            self.interval_ms,
            self.interface.clone(),
            self.ipv4,
            self.ipv6,
        );

        // 执行ping
        let receiver = platform::execute_ping(options)
            .map_err(|e| PyErr::new::<PyRuntimeError, _>(format!("Failed to start ping: {}", e)))?;

        let mut results = Vec::new();
        let mut received_count = 0;
        let start_time = std::time::Instant::now();

        while let Ok(result) = receiver.recv() {
            let ping_result: PingResult = result.into();

            // 添加到结果列表
            results.push(ping_result.clone());

            // 如果是退出信号，跳出循环
            if matches!(ping_result, PingResult::PingExited { .. }) {
                break;
            }

            received_count += 1;

            // 检查是否达到指定数量
            if received_count >= count {
                break;
            }

            // 检查是否超时
            if let Some(timeout_duration) = timeout {
                if start_time.elapsed() >= timeout_duration {
                    break;
                }
            }
        }

        Ok(results)
    }

    pub fn __repr__(&self) -> String {
        format!(
            "Pinger(target='{}', interval_ms={}, ipv4={}, ipv6={})",
            self.target, self.interval_ms, self.ipv4, self.ipv6
        )
    }
}
