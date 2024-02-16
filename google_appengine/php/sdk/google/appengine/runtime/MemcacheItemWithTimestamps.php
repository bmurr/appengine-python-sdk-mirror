<?php
/**
 * Copyright 2007 Google Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
/**
 * A memcache item with a value and timestamps.
 */

class MemcacheItemWithTimestamps {

  private $value = null;
  private $expiration_time_sec = null;
  private $last_access_time_sec = null;
  private $delete_lock_time_sec = null;

  /**
   * Constructs an instance of MemcacheItemWithTimestamps.
   * @param mixed $value The value of the item.
   * @param int $expirationTimeSec The absolute expiration time of the item.
   * @param int $lastAccessTimeSec The absolute last access time of the item.
   * @param int $deleteLockTimeSec The absolute delete lock time of the item.
   */
  public function __construct($value,
                              $expirationTimeSec,
                              $lastAccessTimeSec,
                              $deleteLockTimeSec) {
    $this->value = $value;
    $this->expiration_time_sec = $expirationTimeSec;
    $this->last_access_time_sec = $lastAccessTimeSec;
    $this->delete_lock_time_sec = $deleteLockTimeSec;
  }

  /**
  * @return mixed The value of the item is returned, or empty string if
  * deleted/not found.
  */
  public function getValue() {
    return $this->value;
  }

  /**
  * @return int Absolute expiration timestamp of the item in unix epoch seconds.
  *             Returns 0 if this item has no expiration timestamp.
  */
  public function getExpirationTimeSec() {
    return $this->expiration_time_sec;
  }

  /**
  * @return int Absolute last accessed timestamp of the item in unix epoch
  *             seconds.
  */
  public function getLastAccessTimeSec() {
    return $this->last_access_time_sec;
  }

  /**
  * @return int Absolute delete_time timestamp of the item in unix epoch
  *             seconds. Returns 0 if this item has no expiration timestamp.
  */
  public function getDeleteLockTimeSec() {
    return $this->delete_lock_time_sec;
  }
}