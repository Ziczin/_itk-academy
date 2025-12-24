import asyncio
import sys
from typing import Callable, Optional

import pytest
from test_services.manager import WalletManager
from tqdm import tqdm


@pytest.fixture
async def wallet_manager(client):
    return WalletManager(client)


async def concurrent_operations(
    wallet_manager,
    wallet_id,
    operation_type,
    count=10,
    progress_callback: Optional[Callable] = None,
):
    """Выполняет операции с возможностью отслеживания прогресса"""
    tasks = []
    for _ in range(count):
        task = wallet_manager.post_wallet_operation(
            wallet_id, json={"operation_type": operation_type, "amount": 1.0}
        )

        # Оборачиваем задачу для отслеживания завершения
        if progress_callback:

            async def tracked_task(original_task):
                try:
                    result = await original_task
                    return result
                finally:
                    if progress_callback:
                        progress_callback()

            tasks.append(tracked_task(task))
        else:
            tasks.append(task)

    return await asyncio.gather(*tasks)


async def concurrent_mixed_operations(
    wallet_manager, wallet_id, batch_size, progress_callback: Optional[Callable] = None
):
    """Выполняет смешанные операции с возможностью отслеживания прогресса"""
    tasks = []
    for i in range(batch_size):
        withdraw_task = wallet_manager.post_wallet_operation(
            wallet_id, json={"operation_type": "WITHDRAW", "amount": 1.0}
        )

        deposit_task = wallet_manager.post_wallet_operation(
            wallet_id, json={"operation_type": "DEPOSIT", "amount": 1.0}
        )

        if progress_callback:

            async def tracked_withdraw_task(original_task):
                try:
                    result = await original_task
                    return result
                finally:
                    if progress_callback:
                        progress_callback()

            async def tracked_deposit_task(original_task):
                try:
                    result = await original_task
                    return result
                finally:
                    if progress_callback:
                        progress_callback()

            tasks.append(tracked_withdraw_task(withdraw_task))
            tasks.append(tracked_deposit_task(deposit_task))
        else:
            tasks.append(withdraw_task)
            tasks.append(deposit_task)

    return await asyncio.gather(*tasks)


@pytest.mark.highload
@pytest.mark.parametrize(
    "batch_count,requests_per_batch",
    [
        (10, 10),  # Небольшая нагрузка
        (10, 100),  # Большая нагрузка
    ],
)
async def test_concurrent_deposits_batches(
    wallet_manager, batch_count, requests_per_batch
):
    """Тест параллельных пополнений батчами"""
    test_name = f"deposits_{batch_count}x{requests_per_batch}"

    create_response = await wallet_manager.post_wallets(json={})
    create_response_json = create_response.json()
    wallet_id = create_response_json.get("wallet_id")

    initial_deposit = 100000.0
    deposit_response = await wallet_manager.post_wallet_operation(
        wallet_id, json={"operation_type": "DEPOSIT", "amount": initial_deposit}
    )
    assert deposit_response.status_code == 200

    initial_check = await wallet_manager.get_wallet(wallet_id)
    initial_balance = initial_check.json()["balance"]
    assert initial_balance == initial_deposit

    all_results = []
    total_requests = batch_count * requests_per_batch

    with tqdm(
        total=total_requests,
        desc=f"Test: {test_name}",
        unit="req",
        bar_format="{desc}: {percentage:6.2f}%|{bar:50}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        file=sys.stdout,
        leave=False,
        ncols=100,
    ) as pbar:

        def update_progress():
            pbar.update(1)

        for batch_num in range(batch_count):
            results = await concurrent_operations(
                wallet_manager,
                wallet_id,
                "DEPOSIT",
                count=requests_per_batch,
                progress_callback=update_progress,
            )
            all_results.extend(results)

    successful_deposits = 0

    for response in all_results:
        if response.status_code == 200:
            successful_deposits += 1

    final_response = await wallet_manager.get_wallet(wallet_id)
    final_response_json = final_response.json()
    actual_balance = final_response_json["balance"]

    expected_balance = initial_deposit + successful_deposits * 1.0

    print(
        f"✓ Test {test_name} завершен. Успешных пополнений: {successful_deposits}, "
        f"Баланс: {actual_balance}"
    )

    assert actual_balance == expected_balance


@pytest.mark.highload
@pytest.mark.parametrize(
    "batch_count,requests_per_batch",
    [
        (10, 10),  # Небольшая нагрузка
        (10, 100),  # Большая нагрузка
    ],
)
async def test_concurrent_withdrawals_batches(
    wallet_manager, batch_count, requests_per_batch
):
    """Тест параллельных списаний батчами"""
    test_name = f"withdrawals_{batch_count}x{requests_per_batch}"

    create_response = await wallet_manager.post_wallets(json={})
    create_response_json = create_response.json()
    wallet_id = create_response_json.get("wallet_id")

    initial_deposit = 100000.0
    deposit_response = await wallet_manager.post_wallet_operation(
        wallet_id, json={"operation_type": "DEPOSIT", "amount": initial_deposit}
    )
    assert deposit_response.status_code == 200

    initial_check = await wallet_manager.get_wallet(wallet_id)
    initial_balance = initial_check.json()["balance"]
    assert initial_balance == initial_deposit

    all_results = []
    total_requests = batch_count * requests_per_batch

    with tqdm(
        total=total_requests,
        desc=f"Test: {test_name}",
        unit="req",
        bar_format="{desc}: {percentage:6.2f}%|{bar:50}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        file=sys.stdout,
        leave=False,
        ncols=100,
    ) as pbar:

        def update_progress():
            pbar.update(1)

        for batch_num in range(batch_count):
            results = await concurrent_operations(
                wallet_manager,
                wallet_id,
                "WITHDRAW",
                count=requests_per_batch,
                progress_callback=update_progress,
            )
            all_results.extend(results)

    successful_withdrawals = 0
    failed_withdrawals = 0

    for response in all_results:
        if response.status_code == 200:
            successful_withdrawals += 1
        elif response.status_code == 400:
            failed_withdrawals += 1

    final_response = await wallet_manager.get_wallet(wallet_id)
    final_response_json = final_response.json()
    actual_balance = final_response_json["balance"]

    expected_balance = initial_deposit - successful_withdrawals * 1.0

    print(
        f"✓ Test {test_name} завершен. Успешных списаний: {successful_withdrawals}, "
        f"Неудачных: {failed_withdrawals}, Баланс: {actual_balance}"
    )

    assert actual_balance == expected_balance


@pytest.mark.highload
@pytest.mark.parametrize(
    "batch_count,batch_size",
    [
        (10, 10),  # Небольшая нагрузка
        (10, 100),  # Большая нагрузка
    ],
)
async def test_concurrent_mixed_operations_batches(
    wallet_manager, batch_count, batch_size
):
    """Тест параллельных смешанных операций батчами"""
    test_name = f"mixed_{batch_count}x{batch_size}"

    create_response = await wallet_manager.post_wallets(json={})
    create_response_json = create_response.json()
    wallet_id = create_response_json.get("wallet_id")

    initial_deposit = 100000.0
    deposit_response = await wallet_manager.post_wallet_operation(
        wallet_id, json={"operation_type": "DEPOSIT", "amount": initial_deposit}
    )
    assert deposit_response.status_code == 200

    initial_check = await wallet_manager.get_wallet(wallet_id)
    initial_balance = initial_check.json()["balance"]
    assert initial_balance == initial_deposit

    all_results = []
    total_requests = batch_count * batch_size * 2  # Каждый батч содержит 2 операции

    with tqdm(
        total=total_requests,
        desc=f"Test: {test_name}",
        unit="op",
        bar_format="{desc}: {percentage:6.2f}%|{bar:50}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        file=sys.stdout,
        leave=False,
        ncols=100,
    ) as pbar:

        def update_progress():
            pbar.update(1)

        for batch_num in range(batch_count):
            results = await concurrent_mixed_operations(
                wallet_manager, wallet_id, batch_size, progress_callback=update_progress
            )
            all_results.extend(results)

    successful_withdrawals = 0
    failed_withdrawals = 0
    successful_deposits = 0

    for response in all_results:
        if response.status_code == 200:
            response_json = response.json()
            if response_json["operation_type"] == "WITHDRAW":
                successful_withdrawals += 1
            elif response_json["operation_type"] == "DEPOSIT":
                successful_deposits += 1
        elif response.status_code == 400:
            failed_withdrawals += 1

    final_response = await wallet_manager.get_wallet(wallet_id)
    final_response_json = final_response.json()
    actual_balance = final_response_json["balance"]

    expected_balance = (
        initial_deposit - successful_withdrawals * 1.0 + successful_deposits * 1.0
    )

    print(
        f"✓ {test_name} Успешные списания: {successful_withdrawals}, "
        + f"Успешные пополнения: {successful_deposits}, "
        + f"Баланс: {actual_balance}"
    )

    assert actual_balance == expected_balance
