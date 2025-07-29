pub mod attributes;
pub mod edges;
pub mod nodes;
pub mod traits;
pub mod values;
pub mod wrapper;

use super::{EdgeIndex, MedRecord, MedRecordAttribute, MedRecordValue, NodeIndex, Wrapper};
use crate::errors::MedRecordResult;
use attributes::{
    EdgeAttributesTreeOperand, EdgeMultipleAttributesOperand, EdgeSingleAttributeOperand,
    GetAllAttributes, GetAttributes, NodeAttributesTreeOperand, NodeMultipleAttributesOperand,
    NodeSingleAttributeOperand,
};
use edges::{EdgeIndexOperand, EdgeIndicesOperand, EdgeOperand};
use nodes::{NodeIndexOperand, NodeIndicesOperand, NodeOperand};
use std::{
    fmt::{Debug, Display},
    hash::Hash,
};
use values::{
    EdgeMultipleValuesOperand, EdgeSingleValueOperand, GetValues, NodeMultipleValuesOperand,
    NodeSingleValueOperand,
};

macro_rules! impl_return_operand_for_tuples {
    ($($T:ident),+) => {
        impl<'a, $($T: ReturnOperand<'a>),+> ReturnOperand<'a> for ($($T,)+) {
            type ReturnValue = ($($T::ReturnValue,)+);

            #[allow(non_snake_case)]
            fn evaluate(self, medrecord: &'a MedRecord) -> MedRecordResult<Self::ReturnValue> {
                let ($($T,)+) = self;

                $(let $T = $T.evaluate(medrecord)?;)+

                Ok(($($T,)+))
            }
        }
    };
}

macro_rules! impl_iterator_return_operand {
    ($( $Operand:ident => $Item:ty ),* $(,)?) => {
        $(
            impl<'a> ReturnOperand<'a> for Wrapper<$Operand> {
                type ReturnValue = Box<dyn Iterator<Item = $Item> + 'a>;

                fn evaluate(self, medrecord: &'a MedRecord) -> MedRecordResult<Self::ReturnValue> {
                    Ok(Box::new(self.evaluate_backward(medrecord)?))
                }
            }
        )*
    };
}

macro_rules! impl_direct_return_operand {
    ($( $Operand:ident => $ReturnValue:ty ),* $(,)?) => {
        $(
            impl<'a> ReturnOperand<'a> for Wrapper<$Operand> {
                type ReturnValue = $ReturnValue;

                fn evaluate(self, medrecord: &'a MedRecord) -> MedRecordResult<Self::ReturnValue> {
                    self.evaluate_backward(medrecord)
                }
            }
        )*
    };
}

pub trait Index: Eq + Clone + Hash + Display + GetAttributes {}

impl Index for NodeIndex {}

impl Index for EdgeIndex {}

impl<I: Index> Index for &I {}

pub trait Operand: GetAllAttributes<Self::Index> + GetValues<Self::Index> + Debug + Clone {
    type Index: Index;
}

impl Operand for NodeOperand {
    type Index = NodeIndex;
}

impl Operand for EdgeOperand {
    type Index = EdgeIndex;
}

pub(crate) type BoxedIterator<'a, T> = Box<dyn Iterator<Item = T> + 'a>;

#[derive(Debug, Clone)]
pub enum OptionalIndexWrapper<I: Index, T> {
    WithIndex((I, T)),
    WithoutIndex(T),
}

impl<I: Index, T> OptionalIndexWrapper<I, T> {
    pub fn get_value(&self) -> &T {
        match self {
            OptionalIndexWrapper::WithIndex((_, value)) => value,
            OptionalIndexWrapper::WithoutIndex(value) => value,
        }
    }

    pub fn get_index(&self) -> Option<&I> {
        match self {
            OptionalIndexWrapper::WithIndex((index, _)) => Some(index),
            OptionalIndexWrapper::WithoutIndex(_) => None,
        }
    }

    pub fn unpack(self) -> (Option<I>, T) {
        match self {
            OptionalIndexWrapper::WithIndex((index, value)) => (Some(index), value),
            OptionalIndexWrapper::WithoutIndex(value) => (None, value),
        }
    }

    pub fn map<U, F>(self, f: F) -> OptionalIndexWrapper<I, U>
    where
        F: FnOnce(T) -> U,
    {
        match self {
            OptionalIndexWrapper::WithIndex((index, value)) => {
                OptionalIndexWrapper::WithIndex((index, f(value)))
            }
            OptionalIndexWrapper::WithoutIndex(value) => {
                OptionalIndexWrapper::WithoutIndex(f(value))
            }
        }
    }
}

impl<I: Index, T> From<T> for OptionalIndexWrapper<I, T> {
    fn from(value: T) -> Self {
        OptionalIndexWrapper::WithoutIndex(value)
    }
}

impl<I: Index, T> From<(I, T)> for OptionalIndexWrapper<I, T> {
    fn from(value: (I, T)) -> Self {
        OptionalIndexWrapper::WithIndex(value)
    }
}

#[derive(Debug, Clone)]
pub struct Selection<'a, R: ReturnOperand<'a>> {
    medrecord: &'a MedRecord,
    return_operand: R,
}

impl<'a, R: ReturnOperand<'a>> Selection<'a, R> {
    pub fn new_node<Q>(medrecord: &'a MedRecord, query: Q) -> Self
    where
        Q: FnOnce(&mut Wrapper<NodeOperand>) -> R,
    {
        let mut operand = Wrapper::<NodeOperand>::new(None);

        Self {
            medrecord,
            return_operand: query(&mut operand),
        }
    }

    pub fn new_edge<Q>(medrecord: &'a MedRecord, query: Q) -> Self
    where
        Q: FnOnce(&mut Wrapper<EdgeOperand>) -> R,
    {
        let mut operand = Wrapper::<EdgeOperand>::new(None);

        Self {
            medrecord,
            return_operand: query(&mut operand),
        }
    }

    pub fn evaluate(self) -> MedRecordResult<R::ReturnValue> {
        self.return_operand.evaluate(self.medrecord)
    }
}

pub trait ReturnOperand<'a> {
    type ReturnValue;

    fn evaluate(self, medrecord: &'a MedRecord) -> MedRecordResult<Self::ReturnValue>;
}

impl_iterator_return_operand!(
    NodeAttributesTreeOperand     => (&'a NodeIndex, Vec<MedRecordAttribute>),
    EdgeAttributesTreeOperand     => (&'a EdgeIndex, Vec<MedRecordAttribute>),
    NodeMultipleAttributesOperand => (&'a NodeIndex, MedRecordAttribute),
    EdgeMultipleAttributesOperand => (&'a EdgeIndex, MedRecordAttribute),
    EdgeIndicesOperand            => EdgeIndex,
    NodeIndicesOperand            => NodeIndex,
    NodeMultipleValuesOperand     => (&'a NodeIndex, MedRecordValue),
    EdgeMultipleValuesOperand     => (&'a EdgeIndex, MedRecordValue),
);

impl_direct_return_operand!(
    NodeSingleAttributeOperand => Option<OptionalIndexWrapper<&'a NodeIndex, MedRecordAttribute>>,
    EdgeSingleAttributeOperand => Option<OptionalIndexWrapper<&'a EdgeIndex, MedRecordAttribute>>,
    EdgeIndexOperand           => Option<EdgeIndex>,
    NodeIndexOperand           => Option<NodeIndex>,
    NodeSingleValueOperand     => Option<OptionalIndexWrapper<&'a NodeIndex, MedRecordValue>>,
    EdgeSingleValueOperand     => Option<OptionalIndexWrapper<&'a EdgeIndex, MedRecordValue>>,
);

impl_return_operand_for_tuples!(R1, R2);
impl_return_operand_for_tuples!(R1, R2, R3);
impl_return_operand_for_tuples!(R1, R2, R3, R4);
impl_return_operand_for_tuples!(R1, R2, R3, R4, R5);
impl_return_operand_for_tuples!(R1, R2, R3, R4, R5, R6);
impl_return_operand_for_tuples!(R1, R2, R3, R4, R5, R6, R7);
impl_return_operand_for_tuples!(R1, R2, R3, R4, R5, R6, R7, R8);
impl_return_operand_for_tuples!(R1, R2, R3, R4, R5, R6, R7, R8, R9);
impl_return_operand_for_tuples!(R1, R2, R3, R4, R5, R6, R7, R8, R9, R10);
impl_return_operand_for_tuples!(R1, R2, R3, R4, R5, R6, R7, R8, R9, R10, R11);
impl_return_operand_for_tuples!(R1, R2, R3, R4, R5, R6, R7, R8, R9, R10, R11, R12);
impl_return_operand_for_tuples!(R1, R2, R3, R4, R5, R6, R7, R8, R9, R10, R11, R12, R13);
impl_return_operand_for_tuples!(R1, R2, R3, R4, R5, R6, R7, R8, R9, R10, R11, R12, R13, R14);
impl_return_operand_for_tuples!(R1, R2, R3, R4, R5, R6, R7, R8, R9, R10, R11, R12, R13, R14, R15);
