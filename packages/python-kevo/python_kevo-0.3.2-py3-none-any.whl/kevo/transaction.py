"""
Transaction support for the Kevo client.

This module provides transaction functionality for the Kevo client,
including creating, committing, and rolling back transactions.
"""

import grpc
import threading
from typing import Optional, Tuple

from .connection import Connection
from .errors import handle_grpc_error, TransactionError, ValidationError
from .options import ScanOptions
from .proto.kevo import service_pb2
from .scanner import Scanner, TransactionScanIterator


class Transaction:
    """A database transaction."""

    def __init__(self, connection: Connection, tx_id: str, read_only: bool):
        """
        Initialize a transaction.

        Args:
            connection: The connection to use
            tx_id: Transaction ID returned by the server
            read_only: Whether this is a read-only transaction
        """
        self._connection = connection
        self._id = tx_id
        self._read_only = read_only
        self._closed = False
        self._lock = threading.RLock()

    def commit(self) -> None:
        """
        Commit the transaction.
        
        Raises:
            TransactionError: If the transaction fails to commit
            ValidationError: If the transaction is already closed
        """
        with self._lock:
            if self._closed:
                raise ValidationError("Transaction is already closed")

            request = service_pb2.CommitTransactionRequest(transaction_id=self._id)

            try:
                # For transactions with writes, we must use the primary
                # Even for read-only transactions, commit must go to the node that started it
                stub = self._connection.get_write_stub()
                response = stub.CommitTransaction(
                    request, timeout=self._connection.get_timeout()
                )
                self._closed = True

                if not response.success:
                    raise TransactionError("Transaction commit failed")
            except grpc.RpcError as e:
                error = handle_grpc_error(e, "committing transaction")
                
                # If this is a read-only error, try to connect to the primary and retry
                from .errors import ReadOnlyError
                if isinstance(error, ReadOnlyError) and error.primary_address:
                    self._connection.handle_read_only_error(error)
                    
                    # Retry the operation with the primary connection
                    stub = self._connection.get_write_stub()
                    response = stub.CommitTransaction(
                        request, timeout=self._connection.get_timeout()
                    )
                    self._closed = True
                    
                    if not response.success:
                        raise TransactionError("Transaction commit failed")
                    return
                    
                raise error

    def rollback(self) -> None:
        """
        Roll back the transaction.
        
        Raises:
            TransactionError: If the transaction fails to roll back
            ValidationError: If the transaction is already closed
        """
        with self._lock:
            if self._closed:
                raise ValidationError("Transaction is already closed")

            request = service_pb2.RollbackTransactionRequest(transaction_id=self._id)

            try:
                # Rollback should go to the same node that started the transaction
                # For write transactions, this must be the primary
                if self._read_only:
                    stub = self._connection.get_read_stub(read_from_replicas=False)
                else:
                    stub = self._connection.get_write_stub()
                    
                response = stub.RollbackTransaction(
                    request, timeout=self._connection.get_timeout()
                )
                self._closed = True

                if not response.success:
                    raise TransactionError("Transaction rollback failed")
            except grpc.RpcError as e:
                error = handle_grpc_error(e, "rolling back transaction")
                
                # If this is a read-only error, try to connect to the primary and retry
                from .errors import ReadOnlyError
                if isinstance(error, ReadOnlyError) and error.primary_address:
                    self._connection.handle_read_only_error(error)
                    
                    # Retry the operation with the primary connection
                    stub = self._connection.get_write_stub()
                    response = stub.RollbackTransaction(
                        request, timeout=self._connection.get_timeout()
                    )
                    self._closed = True
                    
                    if not response.success:
                        raise TransactionError("Transaction rollback failed")
                    return
                    
                raise error

    def get(self, key: bytes) -> Tuple[Optional[bytes], bool]:
        """
        Get a value within the transaction.

        Args:
            key: The key to get

        Returns:
            A tuple of (value, found) where found is True if the key exists
            
        Raises:
            ValidationError: If the transaction is closed
            TransactionError: If the get operation fails
        """
        with self._lock:
            if self._closed:
                raise ValidationError("Transaction is closed")

            request = service_pb2.TxGetRequest(transaction_id=self._id, key=key)

            try:
                # For read-only transactions, we can use a replica
                # For write transactions, we must use the primary
                if self._read_only:
                    stub = self._connection.get_read_stub(read_from_replicas=True)
                else:
                    stub = self._connection.get_write_stub()
                    
                response = stub.TxGet(
                    request, timeout=self._connection.get_timeout()
                )
                return (response.value, response.found)
            except grpc.RpcError as e:
                raise handle_grpc_error(e, "getting key in transaction")

    def put(self, key: bytes, value: bytes) -> bool:
        """
        Put a key-value pair within the transaction.

        Args:
            key: The key to put
            value: The value to put

        Returns:
            True if the operation succeeded
            
        Raises:
            ValidationError: If the transaction is closed or read-only
            TransactionError: If the put operation fails
        """
        with self._lock:
            if self._closed:
                raise ValidationError("Transaction is closed")

            if self._read_only:
                raise ValidationError("Cannot write to a read-only transaction")

            request = service_pb2.TxPutRequest(
                transaction_id=self._id, key=key, value=value
            )

            try:
                # Write operations must go to the primary
                stub = self._connection.get_write_stub()
                response = stub.TxPut(
                    request, timeout=self._connection.get_timeout()
                )
                return response.success
            except grpc.RpcError as e:
                error = handle_grpc_error(e, "putting key-value in transaction")
                
                # If this is a read-only error, try to connect to the primary and retry
                from .errors import ReadOnlyError
                if isinstance(error, ReadOnlyError) and error.primary_address:
                    self._connection.handle_read_only_error(error)
                    
                    # Retry the operation with the primary connection
                    stub = self._connection.get_write_stub()
                    response = stub.TxPut(
                        request, timeout=self._connection.get_timeout()
                    )
                    return response.success
                    
                raise error

    def delete(self, key: bytes) -> bool:
        """
        Delete a key-value pair within the transaction.

        Args:
            key: The key to delete

        Returns:
            True if the operation succeeded
            
        Raises:
            ValidationError: If the transaction is closed or read-only
            TransactionError: If the delete operation fails
        """
        with self._lock:
            if self._closed:
                raise ValidationError("Transaction is closed")

            if self._read_only:
                raise ValidationError("Cannot delete in a read-only transaction")

            request = service_pb2.TxDeleteRequest(transaction_id=self._id, key=key)

            try:
                # Write operations must go to the primary
                stub = self._connection.get_write_stub()
                response = stub.TxDelete(
                    request, timeout=self._connection.get_timeout()
                )
                return response.success
            except grpc.RpcError as e:
                error = handle_grpc_error(e, "deleting key in transaction")
                
                # If this is a read-only error, try to connect to the primary and retry
                from .errors import ReadOnlyError
                if isinstance(error, ReadOnlyError) and error.primary_address:
                    self._connection.handle_read_only_error(error)
                    
                    # Retry the operation with the primary connection
                    stub = self._connection.get_write_stub()
                    response = stub.TxDelete(
                        request, timeout=self._connection.get_timeout()
                    )
                    return response.success
                    
                raise error

    def scan(self, options: Optional[ScanOptions] = None) -> Scanner:
        """
        Scan keys within the transaction.

        Args:
            options: Options for the scan operation

        Returns:
            A scanner for iterating through the results
            
        Raises:
            ValidationError: If the transaction is closed
        """
        if self._closed:
            raise ValidationError("Transaction is closed")

        if options is None:
            options = ScanOptions()

        return TransactionScanIterator(self._id, self._connection, options, self._read_only)
    
    def is_read_only(self) -> bool:
        """Check if this is a read-only transaction."""
        return self._read_only
    
    def is_closed(self) -> bool:
        """Check if this transaction is closed."""
        return self._closed